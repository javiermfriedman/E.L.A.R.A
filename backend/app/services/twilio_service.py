# twilio_service.py
# Twilio service layer: phone number validation, outbound call creation, and TwiML generation.
# from_number is read from the FROM_NUMBER environment variable.

import os
import re
from urllib.parse import quote

from fastapi import HTTPException, Request
from loguru import logger
from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import Connect, Stream, VoiceResponse

from app.schemas.calls import TwilioCallResult, TwimlRequest, DialoutRequest


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_phone_number(to_number: str):
    if not to_number.startswith("+1"):
        raise HTTPException(status_code=400, detail="Number must start with +1")
    digits_only = re.sub(r"\D", "", to_number)
    if len(digits_only) != 11:
        raise HTTPException(status_code=400, detail="Invalid number length")
    if digits_only[1:4] == "911":
        raise HTTPException(status_code=400, detail="Cannot call emergency numbers")


# ---------------------------------------------------------------------------
# Twilio call
# ---------------------------------------------------------------------------

async def make_twilio_call(dialout_request: DialoutRequest) -> TwilioCallResult:
    to_number = dialout_request.to_number
    from_number = os.getenv("FROM_NUMBER")

    if not from_number:
        raise ValueError("Missing FROM_NUMBER in environment")

    local_server_url = os.getenv("LOCAL_SERVER_URL")
    if not local_server_url:
        raise ValueError("Missing LOCAL_SERVER_URL in environment")

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if not account_sid or not auth_token:
        raise ValueError("Missing Twilio credentials in environment")

    twiml_url = f"{local_server_url}/twiml"
    client = TwilioClient(account_sid, auth_token)
    call = client.calls.create(to=to_number, from_=from_number, url=twiml_url, method="POST")

    logger.info(f"Twilio call created: {call.sid} → {to_number}")
    return TwilioCallResult(call_sid=call.sid, to_number=to_number)


# ---------------------------------------------------------------------------
# TwiML parsing and generation
# ---------------------------------------------------------------------------

async def parse_twiml_request(request: Request) -> TwimlRequest:
    # Twilio sends form data, not JSON (includes CallSid on voice webhooks)
    form_data = await request.form()
    to_number = form_data.get("To")
    from_number = form_data.get("From")
    call_sid = form_data.get("CallSid")
    return TwimlRequest(to_number=to_number, from_number=from_number, call_sid=call_sid)


def get_websocket_url() -> str:
    if os.getenv("ENV", "local").lower() == "local":
        local_server_url = os.getenv("LOCAL_SERVER_URL")
        if not local_server_url:
            raise ValueError("Missing LOCAL_SERVER_URL in environment")
        ws_url = local_server_url.replace("https://", "wss://")
        return f"{ws_url}/ws"
    else:
        logger.warning("If deployed outside us-west, update the websocket URL below.")
        return "wss://api.pipecat.daily.co/ws/twilio"


def generate_twiml(twiml_request: TwimlRequest) -> str:
    websocket_url = get_websocket_url()
    if twiml_request.call_sid:
        sep = "&" if "?" in websocket_url else "?"
        websocket_url = f"{websocket_url}{sep}callSid={quote(twiml_request.call_sid, safe='')}"
    else:
        logger.warning(
            "TwiML webhook missing CallSid; WebSocket will not receive callSid query param"
        )
    logger.debug(f"Generating TwiML with WebSocket URL: {websocket_url}")

    response = VoiceResponse()
    connect = Connect()
    stream = Stream(url=websocket_url)

    stream.parameter(name="to_number", value=twiml_request.to_number)
    stream.parameter(name="from_number", value=twiml_request.from_number)

    if os.getenv("ENV") == "production":
        agent_name = os.getenv("AGENT_NAME")
        org_name = os.getenv("ORGANIZATION_NAME")
        stream.parameter(name="_pipecatCloudServiceHost", value=f"{agent_name}.{org_name}")

    connect.append(stream)
    response.append(connect)
    response.pause(length=20)

    return str(response)