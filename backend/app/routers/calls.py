# calls.py
# Router for all call-related endpoints: dialout, twiml webhook, and websocket.
# Single-call local setup — agent config stored as a simple module-level variable.

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket
from fastapi.responses import HTMLResponse
from loguru import logger
from pipecat.runner.types import WebSocketRunnerArguments
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agents import Agents
from app.pipelines.mark_one import bot
from app.schemas.calls import DialoutRequest, DialoutResponse
from app.services.twilio_service import (
    generate_twiml,
    make_twilio_call,
    parse_twiml_request,
    validate_phone_number,
)

router = APIRouter(tags=["Calls"])

# Single call config — overwritten on each /dialout request
current_call: dict = {}


# ---------------------------------------------------------------------------
# POST /dialout — initiate an outbound call
# ---------------------------------------------------------------------------

@router.post("/dialout", response_model=DialoutResponse)
async def handle_dialout_request(
    dialout_request: DialoutRequest,
    db: Session = Depends(get_db),
):
    global current_call

    validate_phone_number(dialout_request.to_number)

    agent = db.query(Agents).filter(Agents.id == dialout_request.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    call_result = await make_twilio_call(dialout_request)

    current_call = {
        "system_prompt": agent.system_prompt,
        "voice_id": agent.voice_id,
    }
    logger.info(f"Call initiated: {call_result.call_sid}")

    return DialoutResponse(
        call_sid=call_result.call_sid,
        status="call_initiated",
        to_number=call_result.to_number,
    )


# ---------------------------------------------------------------------------
# POST /twiml — Twilio webhooks here to get connection instructions
# ---------------------------------------------------------------------------

@router.post("/twiml")
async def get_twiml(request: Request) -> HTMLResponse:
    logger.info("Serving TwiML for outbound call")
    twiml_request = await parse_twiml_request(request)
    twiml_content = generate_twiml(twiml_request)
    return HTMLResponse(content=twiml_content, media_type="application/xml")


# ---------------------------------------------------------------------------
# WS /ws — Twilio media stream connects here, Pipecat takes over
# ---------------------------------------------------------------------------

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted")

    try:
        runner_args = WebSocketRunnerArguments(websocket=websocket)
        await bot(
            runner_args,
            system_prompt=current_call["system_prompt"],
            voice_id=current_call["voice_id"],
        )
    except Exception as e:
        logger.error(f"Error in WebSocket endpoint: {e}")
        await websocket.close()