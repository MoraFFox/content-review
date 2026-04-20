"""CrewAI crew definition for compliance scanning workflow."""

from crewai import Crew, Task

from banshield.agents.compliance_agent import ComplianceAgent
from banshield.agents.vision_agent import VisionAgent
from banshield.agents.audio_agent import AudioAgent


class ComplianceCrew:
    """Orchestrates agents to perform end-to-end compliance scanning."""

    def __init__(self) -> None:
        self.compliance_agent = ComplianceAgent().agent
        self.vision_agent = VisionAgent().agent
        self.audio_agent = AudioAgent().agent

    def create_tasks(self, video_path: str) -> list[Task]:
        """Create tasks for the compliance scanning workflow."""
        raise NotImplementedError

    def run(self, video_path: str) -> dict:
        """Execute the compliance scanning crew."""
        crew = Crew(
            agents=[self.compliance_agent, self.vision_agent, self.audio_agent],
            tasks=self.create_tasks(video_path),
            verbose=True,
        )
        return crew.kickoff()
