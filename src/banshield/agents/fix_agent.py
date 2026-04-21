"""CrewAI fix suggestion agent implementation."""

import json
import logging

from crewai import Agent

from banshield.core.llm_provider import get_llm

logger = logging.getLogger(__name__)


def generate_fixes(compliance_report_json: str) -> str:
    """Generate actionable fix suggestions for each violation in the compliance report.

    Args:
        compliance_report_json: JSON string containing the compliance report with violations.

    Returns:
        JSON string with a list of fixes: {"violation": "...", "fix": "...", "priority": "high|medium|low"}.
    """
    # The agent itself performs this reasoning via its task description.
    # This tool exists so the agent can declare it has the capability.
    return compliance_report_json


class FixAgent:
    """Agent that generates specific, actionable fix suggestions for violations."""

    def __init__(self) -> None:
        self.agent = Agent(
            role="Ad Fix Strategist",
            goal="For each compliance violation, generate a specific, actionable fix suggestion",
            backstory=(
                "You are an expert ad creative strategist who knows how to fix "
                "compliance issues while preserving the ad's effectiveness. You produce "
                "concrete, prioritized fix suggestions for every violation found."
            ),
            tools=[generate_fixes],
            llm=get_llm(),
            verbose=True,
        )
