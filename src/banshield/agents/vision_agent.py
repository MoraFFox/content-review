"""CrewAI vision analysis agent implementation."""

from crewai import Agent


class VisionAgent:
    """Agent responsible for analyzing video frames and visual content."""

    def __init__(self) -> None:
        self.agent = Agent(
            role="Visual Content Analyst",
            goal="Analyze video frames for compliance issues, branding, and visual claims",
            backstory="You are an expert in visual analysis of advertising content.",
            verbose=True,
        )
