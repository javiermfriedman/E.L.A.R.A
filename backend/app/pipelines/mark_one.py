
import os
import io
import sys
import wave
import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer, VADParams
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask

from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import parse_telephony_websocket
from pipecat.serializers.twilio import TwilioFrameSerializer

from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.processors.audio.audio_buffer_processor import AudioBufferProcessor

from app.models.recordings import Recordings


from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)
from pipecat.frames.frames import TTSSpeakFrame

from app.database import get_db
from app.models.agents import Agents

load_dotenv(override=True)

# from core.prompt_nexus import get_system_prompt

# logger.remove()
# logger.add(
#     sys.stderr,
#     level="DEBUG",
#     filter=lambda record: not record["name"].startswith("pipecat"),
# )

RECORDINGS_DIR = Path("recordings")
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)


def get_wav_bytes(audio: bytes, sample_rate: int, num_channels: int) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)
        wf.writeframes(audio)
    return buffer.getvalue()

async def save_recording(user_id: int, audio: bytes) -> Recordings:
    # 1. Save to local recordings dir
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recording_{user_id}_{timestamp}.wav"
    file_path = RECORDINGS_DIR / filename
    with open(file_path, "wb") as f:
        f.write(audio)
    logger.info(f"Saved recording locally to {file_path}")
    
    db = next(get_db())
    try:
        recording = Recordings(user_id=user_id, audio=audio)
        db.add(recording)
        db.commit()
        db.refresh(recording)
        return recording
    finally:
        db.close()

async def run_bot(
    transport,
    handle_sigint: bool,
    vad: SileroVADAnalyzer,
    system_prompt: str,
    first_message: str,
    user_id: int,
):
    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        settings=OpenAILLMService.Settings(
            model="gpt-4",
        ),
    )

    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        output_format="pcm_8000",
        push_silence_after_stopping=False,
        settings=ElevenLabsTTSService.Settings(
            voice="zmcVlqmyk3Jpn5AVYcAL",
            model="eleven_turbo_v2",
        ),
    )


    logger.info("Initializing Deepgram STT service...")

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        audio_passthrough=True,
        encoding="linear16",
        sample_rate=8000,
        channels=1,
        settings=DeepgramSTTService.Settings(
            model="nova-2-phonecall",
            language="en-US",
            interim_results=True,
        ),
    )

    logger.info("Deepgram STT service initialized")


    audiobuffer = AudioBufferProcessor(
        sample_rate=8000,
        num_channels=2,
        enable_turn_audio=False,
    )

    logger.info(f"System Prompt: {system_prompt}, User ID: {user_id}")

    @audiobuffer.event_handler("on_audio_data")
    async def on_audio_data(buffer, audio: bytes, sample_rate: int, num_channels: int):
        wav_bytes = get_wav_bytes(audio, sample_rate, num_channels)
        await save_recording(user_id, wav_bytes)
        logger.info(f"Saved recording for user {user_id}")

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },  
    ]

    context = LLMContext(messages=messages)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=vad,
        ),
    )

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            llm,
            tts,
            transport.output(),
            audiobuffer,          # must be after transport.output()
            assistant_aggregator,
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=8000,
            audio_out_sample_rate=8000,
            allow_interruptions=True,
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected - outbound call active")
        await audiobuffer.start_recording()
        await task.queue_frames(
            [TTSSpeakFrame(text=first_message)]
        )

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("on_client_disconnected fired")
        try:
            logger.info("Calling stop_recording...")
            await audiobuffer.stop_recording()
            logger.info("stop_recording complete")
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
        finally:
            await task.cancel()

    runner = PipelineRunner(handle_sigint=handle_sigint)
    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    transport_type, call_data = await parse_telephony_websocket(runner_args.websocket)

    body_data = call_data.get("body", {})
    to_number = body_data.get("to_number")
    from_number = body_data.get("from_number")
    agent_id = body_data.get("agent_id")    # <-- add this
    user_id = body_data.get("user_id")      # <-- add this

    logger.info(f"Call - To: {to_number}, From: {from_number}, Agent ID: {agent_id}, User ID: {user_id}")

    serializer = TwilioFrameSerializer(
        stream_sid=call_data["stream_id"],
        call_sid=call_data["call_id"],
        account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
        auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
    )

    vad = SileroVADAnalyzer(
        params=VADParams(
            start_secs=0.10,
            stop_secs=0.30,
            confidence=0.65,
        )
    )

    transport = FastAPIWebsocketTransport(
        websocket=runner_args.websocket,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,
            serializer=serializer,
        ),
    )
    db = next(get_db())
    agent = db.query(Agents).filter(Agents.id == agent_id).filter(Agents.owner_id == user_id).first()
    if not agent:
        logger.error(f"Agent not found for user {user_id} and agent  {agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")
    
    system_prompt = agent.system_prompt
    first_message = agent.first_message
    await run_bot(transport, runner_args.handle_sigint, vad, system_prompt, first_message, user_id)