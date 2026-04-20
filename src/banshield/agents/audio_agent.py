"""CrewAI audio analysis agent implementation."""

from crewai import Agent


class AudioAgent:
    """Agent responsible for analyzing audio and transcription content."""

    def __init__(self) -> None:
        self.agent = Agent(
            role="Audio Content Analyst",
            goal="Analyze audio transcripts and claims for compliance issues",
            backstory="You are an expert in audio analysis and transcription review.",
            verbose=True,
        )
