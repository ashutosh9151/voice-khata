"""
Voice Khata - Full Voice Agent using Pipecat + Gnani
====================================================
Required:
  - Gnani Prisma v3.0 (STT)
  - Gnani Timbre v3.0 (TTS)
  - WebSocket streaming
  - Open LLM (Groq recommended for speed)

Run:
  python bot.py

For browser testing use Daily transport or SmallWebRTC.
"""

import os
import asyncio
from dotenv import load_dotenv

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.services.groq.llm import GroqLLMService
from pipecat.transcriptions.language import Language
from pipecat_gnani import GnaniSTTService, GnaniTTSService

from ledger import process_command
from prompts.system_prompt import SYSTEM_PROMPT

load_dotenv()


async def main():
    # --------------------------------------------------
    # 1. STT - Gnani Prisma v3.0 (Required by challenge)
    # --------------------------------------------------
    stt = GnaniSTTService(
        api_key=os.getenv("GNANI_API_KEY"),
        settings=GnaniSTTService.Settings(
            model="prisma-v3.0",
            language="indic-auto",          # Auto detect Hindi/English mix
            language_candidates=[Language.HI_IN, Language.EN_IN],
            sample_rate=16000,
        ),
    )

    # --------------------------------------------------
    # 2. TTS - Gnani Timbre v3.0 (Required by challenge)
    # --------------------------------------------------
    tts = GnaniTTSService(
        api_key=os.getenv("GNANI_API_KEY"),
        settings=GnaniTTSService.Settings(
            model="timbre-v3.0",
            voice="Avinash",                # Clear male voice good for shop
            language=Language.HI_IN,
            speed=1.05,
        ),
    )

    # --------------------------------------------------
    # 3. LLM - Fast model (Groq recommended)
    # --------------------------------------------------
    llm = GroqLLMService(
        api_key=os.getenv("GROQ_API_KEY"),
        settings=GroqLLMService.Settings(
            model="llama-3.3-70b-versatile",  # or llama-3.1-8b-instant for speed
        ),
    )

    # --------------------------------------------------
    # 4. Context + Aggregators
    # --------------------------------------------------
    context = LLMContext(messages=[
        {"role": "system", "content": SYSTEM_PROMPT}
    ])

    aggregators = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer()
        ),
    )

    # --------------------------------------------------
    # Note: For full browser/mic transport you need to
    # add DailyTransport or SmallWebRTCTransport.
    # See docs.pipecat.ai for transport examples.
    # --------------------------------------------------
    print("=" * 55)
    print("  Khata Mitra Voice Agent")
    print("  STT : Gnani Prisma v3.0")
    print("  TTS : Gnani Timbre v3.0")
    print("  LLM : Groq")
    print("=" * 55)
    print("\nThis is the core pipeline setup.")
    print("Add a transport (Daily / WebRTC) to make it live.")
    print("For quick testing use: python main.py (text mode)\n")


if __name__ == "__main__":
    asyncio.run(main())
