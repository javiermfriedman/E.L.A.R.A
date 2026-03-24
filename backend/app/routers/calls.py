#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""calls.py

Router to handle outbound call requests, initiate calls via Twilio API,
and handle subsequent WebSocket connections for Media Streams.
"""

from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import HTMLResponse
from loguru import logger
from app.services.twilio_service import (
    DialoutResponse,
    generate_twiml,
    make_twilio_call,
    parse_twiml_request,
    verify_agent,
)

from app.pipelines.mark_one import bot
from pipecat.runner.types import WebSocketRunnerArguments

from app.dependencies import db_dependency, user_dependency
from app.schemas.calls import DialoutRequest

router = APIRouter()



@router.post("/dialout", response_model=DialoutResponse)
async def handle_dialout_request(db: db_dependency, user: user_dependency, dialout_request: DialoutRequest) -> DialoutResponse:
    """handle outbound call request and initiate call via Twilio.
    """
    logger.info(f"Received outbound call request with data: {dialout_request}")

    agent = verify_agent(dialout_request.agent_id, db)
    call_result = await make_twilio_call(user["id"], dialout_request.agent_id, dialout_request.to_number)

    return DialoutResponse(
        call_sid=call_result.call_sid,
        status="call_initiated",
        to_number=call_result.to_number,
    )


@router.post("/twiml")
async def get_twiml(request: Request) -> HTMLResponse:
    """Return TwiML instructions for connecting call to WebSocket.

    This endpoint is called by Twilio when a call is initiated. It returns TwiML
    that instructs Twilio to connect the call to our WebSocket endpoint with
    stream parameters containing call metadata.

    Args:
        request (Request): FastAPI request containing Twilio form data with 'To' and 'From'.
        agent_id (str): Agent id for the outbound call context.
        user_id (str): Authenticated user id.

    Returns:
        HTMLResponse: TwiML XML response with Stream connection instructions.
    """
    logger.info("Serving TwiML for outbound call")

    # Read the params you encoded in the URL during /dialout
    agent_id = request.query_params.get("agent_id")
    user_id = request.query_params.get("user_id")

    twiml_request = await parse_twiml_request(request)
    twiml_content = generate_twiml(twiml_request, agent_id, user_id)

    return HTMLResponse(content=twiml_content, media_type="application/xml")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connection from Twilio Media Streams.

    This endpoint receives the WebSocket connection from Twilio's Media Streams
    and runs the bot to handle the voice conversation. Stream parameters passed
    from TwiML are available to the bot for customization.

    Args:
        websocket (WebSocket): FastAPI WebSocket connection from Twilio.
    """
    await websocket.accept()
    logger.info("WebSocket connection accepted for outbound call")

    try:
        runner_args = WebSocketRunnerArguments(websocket=websocket)
        logger.info(f"Runner args: {runner_args}")
        await bot(runner_args)
        logger.info("Bot finished running")
    except Exception as e:
        logger.error(f"Error in WebSocket endpoint: {e}")
        await websocket.close()