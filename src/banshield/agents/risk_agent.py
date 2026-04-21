"""CrewAI risk scoring agent implementation."""

import json
import logging

from crewai import Agent

from banshield.core.llm_provider import get_llm

logger = logging.getLogger(__name__)


def compute_risk_score(all_outputs_json: str) -> str:
    """Compute overall compliance risk score from all agent outputs.

    Args:
        all_outputs_json: JSON string containing vision, audio, compliance, and fix outputs.

    Returns:
        JSON string with overall_score (0-100), risk_level (low/medium/high/critical), and breakdown.
    """
    # The agent itself performs this reasoning via its task description.
    return all_outputs_json


class RiskAgent:
    """Agent that computes the final compliance risk score."""

    def __init__(self) -> None:
        self.agent = Agent(
            role="Risk Scorer",
            goal=(
                "Take all agent outputs and compute an overall compliance score (0-100) "
                "and risk level. Visual violations = 40%, audio violations = 30%, "
                "policy violations = 30%."
            ),
            backstory=(
                "You are a senior compliance risk analyst who quantifies advertising "
                "risk using weighted scoring models. You produce clear, defensible scores."
            ),
            tools=[compute_risk_score],
            llm=get_llm(),
            verbose=True,
        )
