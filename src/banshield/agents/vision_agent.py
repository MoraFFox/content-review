"""CrewAI vision analysis agent implementation."""

import asyncio
import concurrent.futures
import json
import logging

from crewai import Agent

from banshield.core.llm_provider import get_llm
from banshield.services.vision_service import VisionService

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a sync context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return executor.submit(asyncio.run, coro).result()


def analyze_frames(frame_paths: list[str]) -> str:
    """Analyze video frames for visual compliance issues.

    Args:
        frame_paths: List of absolute paths to extracted video frames.

    Returns:
        JSON string with findings including issue types, descriptions, and severity.
    """
    service = VisionService()
    results = _run_async(service.analyze_frames(frame_paths))
    return json.dumps(results, indent=2)


class VisionAgent:
    """Agent responsible for analyzing video frames and visual content."""

    def __init__(self) -> None:
        self.agent = Agent(
            role="Visual Content Analyst",
            goal="Analyze video frames for compliance issues, branding, and visual claims",
            backstory=(
                "You are an expert in visual analysis of advertising content. "
                "You identify explicit content, misleading claims, prohibited products, "
                "text overlays, and brand safety issues in video frames."
            ),
            tools=[analyze_frames],
            llm=get_llm(),
            verbose=True,
        )
