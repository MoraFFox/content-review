"""CrewAI compliance agent implementation."""

from crewai import Agent


class ComplianceAgent:
    """Agent responsible for evaluating ad compliance against regulations."""

    def __init__(self) -> None:
        self.agent = Agent(
            role="Compliance Reviewer",
            goal="Identify regulatory violations in video advertisements",
            backstory="You are an expert in advertising regulations and compliance standards.",
            verbose=True,
        )
