"""CrewAI audio analysis agent implementation."""

import asyncio
import concurrent.futures
import json
import logging

from crewai import Agent

from banshield.core.llm_provider import get_llm
from banshield.services.whisper_service import WhisperService
from banshield.services.azure_reasoning import AzureReasoningService

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a sync context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return executor.submit(asyncio.run, coro).result()


def transcribe_and_analyze(audio_path: str) -> str:
    """Transcribe audio and analyze the transcript for compliance issues.

    Args:
        audio_path: Absolute path to the extracted audio WAV file.

    Returns:
        JSON string with transcript text, segments, and identified audio violations.
    """
    whisper = WhisperService()
    transcript = whisper.transcribe(audio_path)

    reasoning = AzureReasoningService()
    analysis = _run_async(
        reasoning.evaluate_compliance(
            transcript["text"],
            rules=[
                "misleading claims",
                "prohibited language",
                "false advertising",
                "unsubstantiated health claims",
            ],
        )
    )

    result = {
        "transcript": transcript["text"],
        "language": transcript["language"],
        "violations": analysis.get("violations", []),
    }
    return json.dumps(result, indent=2)


class AudioAgent:
    """Agent responsible for analyzing audio and transcription content."""

    def __init__(self) -> None:
        self.agent = Agent(
            role="Audio Content Analyst",
            goal="Analyze audio transcripts and claims for compliance issues",
            backstory=(
                "You are an expert in audio analysis and transcription review. "
                "You identify misleading claims, prohibited language, and false "
                "advertising in spoken ad content."
            ),
            tools=[transcribe_and_analyze],
            llm=get_llm(),
            verbose=True,
        )
