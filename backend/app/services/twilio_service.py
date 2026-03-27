#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import os

from fastapi import HTTPException, Request
from loguru import logger
from pydantic import BaseModel
from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import Connect, Stream, VoiceResponse

from app.dependencies import db_dependency
from app.models.agents import Agents
from app.schemas.agents import AgentResponse
from app.schemas.calls import TwilioCallResult, TwimlRequest






def verify_agent(agent_id: str, db: db_dependency) -> AgentResponse:
    """Verify that the agent exists and is owned by the user.

    Args:
        agent_id (str): The ID of the agent to verify.
        db (db_dependency): The database dependency.

    Returns:
        AgentResponse: The verified agent.
    """
    agent = db.query(Agents).filter(Agents.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse.model_validate(agent)

async def make_twilio_call(
    user_id: int | str,
    agent_id: str,
    to_number: str,
    target_name: str,
) -> TwilioCallResult:
    """Initiate an outbound call via Twilio API.

    Creates a Twilio call that will request TwiML from the /twiml endpoint,
    which then connects the call to the WebSocket endpoint for bot handling.

    Args:
        user_id: Authenticated user id (may be int or str depending on auth).
        agent_id: Agent id for the outbound call context.
        to_number: Destination E.164 number.
        target_name: Name of the target.
    Returns:
        TwilioCallResult: Result containing the call SID and destination number.

    Raises:
        ValueError: If required environment variables are missing.
    """
    from_number = os.getenv("TWILIO_FROM_NUMBER")

    # has to be ngrok url
    local_server_url = os.getenv("LOCAL_SERVER_URL")
    if not local_server_url:
        raise ValueError("Missing LOCAL_SERVER_URL")

    # Encode agent_id and user_id as query params
    twiml_url = (
        f"{local_server_url}/twiml"
        f"?agent_id={agent_id}"
        f"&user_id={user_id}"
        f"&target_name={target_name}"
    )
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        raise ValueError("Missing Twilio credentials")

    logger.info(f"Making Twilio call to {to_number} from {from_number} with URL {twiml_url}")
    
    # Create Twilio client and make the call
    client = TwilioClient(account_sid, auth_token)
    call = client.calls.create(to=to_number, from_=from_number, url=twiml_url, method="POST")

    return TwilioCallResult(call_sid=call.sid, to_number=to_number)

async def parse_twiml_request(request: Request) -> TwimlRequest:
    """Parse and validate TwiML request data from Twilio.

    Twilio sends webhook data as form-encoded data, not JSON. This function
    extracts the 'To' and 'From' phone numbers from the form data.

    Args:
        request (Request): FastAPI request object containing Twilio form data.

    Returns:
        TwimlRequest: Parsed TwiML request with phone number metadata.
    """
    # Twilio sends form data, not JSON
    form_data = await request.form()
    to_number = form_data.get("To")
    from_number = form_data.get("From")

    return TwimlRequest(to_number=to_number, from_number=from_number)


def get_websocket_url() -> str:
    """Get the appropriate WebSocket URL based on environment.

    Returns the local WebSocket URL for local development or the Pipecat Cloud
    URL for production deployments.

    Returns:
        str: WebSocket URL (wss://) for Twilio Media Streams to connect to.

    Raises:
        ValueError: If LOCAL_SERVER_URL is missing in local environment.
    """
    if os.getenv("ENV", "local").lower() == "local":
        local_server_url = os.getenv("LOCAL_SERVER_URL")
        if not local_server_url:
            raise ValueError("Missing LOCAL_SERVER_URL")
        # Convert https:// to wss://
        ws_url = local_server_url.replace("https://", "wss://")
        return f"{ws_url}/ws"
    else:
        print("If deployed in a region other than us-west (default), update websocket url!")

        ws_url = "wss://api.pipecat.daily.co/ws/twilio"
        # uncomment appropriate region url:
        # ws_url = wss://us-east.api.pipecat.daily.co/ws/twilio
        # ws_url = wss://eu-central.api.pipecat.daily.co/ws/twilio
        # ws_url = wss://ap-south.api.pipecat.daily.co/ws/twilio
        return ws_url


def generate_twiml(twiml_request: TwimlRequest, agent_id: str, user_id: str, target_name: str) -> str:
    """Generate TwiML response with WebSocket Stream connection.

    Creates TwiML that instructs Twilio to connect the call to our WebSocket
    endpoint. Call metadata (to_number, from_number) is passed as stream
    parameters, making them available to the bot for customization.

    Args:
        twiml_request (TwimlRequest): Request containing call metadata (phone numbers).
        agent_id (str): Agent id for the outbound call context.
        user_id (str): Authenticated user id.
        target_name (str): Name of the target.
    Returns:
        str: TwiML XML string with Stream connection and parameters.
    """
    websocket_url = get_websocket_url()
    logger.debug(f"Generating TwiML with WebSocket URL: {websocket_url}")

    # Create TwiML response
    response = VoiceResponse()
    connect = Connect()
    stream = Stream(url=websocket_url)

    # Add call metadata as stream parameters so the bot can access them
    # These will be available in the WebSocket 'start' message
    stream.parameter(name="to_number", value=twiml_request.to_number)
    stream.parameter(name="from_number", value=twiml_request.from_number)
    stream.parameter(name="agent_id", value=agent_id)
    stream.parameter(name="user_id", value=user_id)
    stream.parameter(name="target_name", value=target_name)
    connect.append(stream)
    response.append(connect)
    response.pause(length=20)

    return str(response)