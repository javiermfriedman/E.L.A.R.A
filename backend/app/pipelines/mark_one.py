# mark_one.py
# Core Pipecat pipeline for AI voice calls.
# Handles STT, LLM, TTS, and call recording.

import os
import wave
import datetime
from pathlib import Path

from dotenv import load_dotenv
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
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)
from pipecat.frames.frames import TTSSpeakFrame

load_dotenv(override=True)

RECORDINGS_DIR = Path("recordings")
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def save_wav(filename: Path, audio: bytes, sample_rate: int, num_channels: int) -> None:
    with wave.open(str(filename), "wb") as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------

async def run_bot(
    transport,
    handle_sigint: bool,
    vad: SileroVADAnalyzer,
    call_sid: str,
    to_number: str,
    system_prompt: str,
    voice_id: str,
):
    if not voice_id:
        voice_id = "zmcVlqmyk3Jpn5AVYcAL"
    if not system_prompt:
        system_prompt = "You are a helpful assistant."

    logger.info(f"Call SID: {call_sid}")
    logger.info(f"System prompt: {system_prompt}")
    logger.info(f"Voice ID: {voice_id}")

    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        settings=OpenAILLMService.Settings(model="gpt-4"),
    )

    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        output_format="pcm_8000",
        push_silence_after_stopping=False,
        settings=ElevenLabsTTSService.Settings(
            voice=voice_id,
            model="eleven_turbo_v2",
        ),
    )

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

    # Stereo merged output: user on left, bot on right
    audiobuffer = AudioBufferProcessor(
        sample_rate=8000,
        num_channels=2,
        enable_turn_audio=False,
    )

    @audiobuffer.event_handler("on_audio_data")
    async def on_audio_data(buffer, audio: bytes, sample_rate: int, num_channels: int):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = RECORDINGS_DIR / f"{call_sid}_{timestamp}_merged.wav"
        save_wav(filename, audio, sample_rate, num_channels)
        logger.info(f"Saved merged recording: {filename}")

    @audiobuffer.event_handler("on_track_audio_data")
    async def on_track_audio_data(
        buffer,
        user_audio: bytes,
        bot_audio: bytes,
        sample_rate: int,
        num_channels: int,
    ):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        user_file = RECORDINGS_DIR / f"{call_sid}_{timestamp}_user.wav"
        bot_file = RECORDINGS_DIR / f"{call_sid}_{timestamp}_bot.wav"
        save_wav(user_file, user_audio, sample_rate, 1)
        save_wav(bot_file, bot_audio, sample_rate, 1)
        logger.info(f"Saved user track: {user_file}")
        logger.info(f"Saved bot track: {bot_file}")

    messages = [{"role": "system", "content": system_prompt}]

    context = LLMContext(messages=messages)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(vad_analyzer=vad),
    )

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            llm,
            tts,
            transport.output(),
            audiobuffer,           # must be after transport.output()
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
        logger.info("Client connected — outbound call active")
        await audiobuffer.start_recording()
        await task.queue_frames(
            [TTSSpeakFrame(text="Hello! My name is Elara. How are you today?")]
        )

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Client disconnected — outbound call ended")
        try:
            await audiobuffer.stop_recording()
        finally:
            await task.cancel()

    runner = PipelineRunner(handle_sigint=handle_sigint)
    await runner.run(task)


# ---------------------------------------------------------------------------
# Bot entrypoint — called directly from calls.py
# ---------------------------------------------------------------------------

async def bot(runner_args: RunnerArguments, system_prompt: str, voice_id: str):
    transport_type, call_data = await parse_telephony_websocket(runner_args.websocket)

    body_data = call_data.get("body", {})
    to_number = body_data.get("to_number")
    from_number = body_data.get("from_number")
    call_sid = call_data["call_id"]

    logger.info(f"Call — To: {to_number}, From: {from_number}")

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

    await run_bot(
        transport,
        runner_args.handle_sigint,
        vad,
        call_sid,
        to_number,
        system_prompt,
        voice_id,
    )