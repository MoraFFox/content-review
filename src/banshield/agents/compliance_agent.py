"""CrewAI compliance agent implementation."""

import asyncio
import concurrent.futures
import json
import logging

from crewai import Agent

from banshield.core.llm_provider import get_llm
from banshield.services.policy_retriever import PolicyRetriever

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a sync context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return executor.submit(asyncio.run, coro).result()


def check_against_policies(findings_json: str, platform: str = "both") -> str:
    """Retrieve relevant policies and map findings to actual policy rules.

    Args:
        findings_json: JSON string containing vision and audio analysis results.
        platform: Target platform ('meta', 'tiktok', or 'both').

    Returns:
        JSON string with a structured compliance report including mapped violations.
    """
    retriever = PolicyRetriever()
    platforms = ["meta", "tiktok"] if platform == "both" else [platform]

    all_policies: list[str] = []
    for p in platforms:
        chunks = _run_async(retriever.retrieve(findings_json, platform=p, top_k=5))
        all_policies.extend(chunks)

    # Let the agent do the mapping with policy context available
    result = {
        "platform": platform,
        "policy_chunks_consulted": len(all_policies),
        "policies": all_policies,
        "raw_findings": findings_json,
    }
    return json.dumps(result, indent=2)


class ComplianceAgent:
    """Agent responsible for evaluating ad compliance against regulations."""

    def __init__(self) -> None:
        self.agent = Agent(
            role="Compliance Reviewer",
            goal="Identify regulatory violations in video advertisements and map them to platform policies",
            backstory=(
                "You are an expert in advertising regulations and compliance standards. "
                "You cross-reference ad content findings with Meta and TikTok advertising "
                "policies to produce detailed compliance reports."
            ),
            tools=[check_against_policies],
            llm=get_llm(),
            verbose=True,
        )
