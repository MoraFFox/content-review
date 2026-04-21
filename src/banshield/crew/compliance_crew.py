"""CrewAI crew definition for compliance scanning workflow."""

import json
import logging
from datetime import datetime, timezone

from crewai import Crew, Task

from banshield.agents.compliance_agent import ComplianceAgent
from banshield.agents.vision_agent import VisionAgent
from banshield.agents.audio_agent import AudioAgent
from banshield.agents.fix_agent import FixAgent
from banshield.agents.risk_agent import RiskAgent

logger = logging.getLogger(__name__)


class ComplianceCrew:
    """Orchestrates agents to perform end-to-end compliance scanning."""

    def __init__(self, platform: str = "both") -> None:
        self.platform = platform
        self.compliance_agent = ComplianceAgent().agent
        self.vision_agent = VisionAgent().agent
        self.audio_agent = AudioAgent().agent
        self.fix_agent = FixAgent().agent
        self.risk_agent = RiskAgent().agent

    def create_tasks(
        self, frames: list[str], audio_path: str, scan_id: str
    ) -> list[Task]:
        """Create tasks for the compliance scanning workflow."""
        task_vision = Task(
            description=(
                f"Analyze the following video frames for visual compliance issues. "
                f"Call the analyze_frames tool with these frame paths: {frames}. "
                f"Identify explicit content, misleading claims, prohibited products, "
                f"text overlays, and brand safety issues. Return a structured JSON list "
                f'of findings with fields: "issue_type", "description", "severity". '
                f"Platform: {self.platform}."
            ),
            expected_output=(
                "JSON array of visual findings. Example: [{\"issue_type\": \"prohibited_product\", "
                "\"description\": \"Depicts tobacco use\", \"severity\": \"high\"}]"
            ),
            agent=self.vision_agent,
        )

        task_audio = Task(
            description=(
                f"Transcribe and analyze the audio from this video. "
                f"Call the transcribe_and_analyze tool with audio_path='{audio_path}'. "
                f"Identify misleading claims, prohibited language, false advertising, "
                f"and unsubstantiated health claims. Return structured findings."
            ),
            expected_output=(
                "JSON object with transcript text and list of audio violations."
            ),
            agent=self.audio_agent,
            context=[task_vision],
        )

        task_compliance = Task(
            description=(
                f"Review the vision and audio analysis results. "
                f"Call the check_against_policies tool with the combined findings and "
                f"platform='{self.platform}'. Map each violation to actual Meta or TikTok "
                f"advertising policy rules. Return a structured compliance report with "
                f"policy references for each violation."
            ),
            expected_output=(
                "JSON compliance report with mapped violations and policy references."
            ),
            agent=self.compliance_agent,
            context=[task_vision, task_audio],
        )

        task_fix = Task(
            description=(
                "Take the compliance report and generate specific, actionable fix "
                "suggestions for each violation. Call the generate_fixes tool with the "
                "compliance report. Each fix must include the violation description, "
                "the suggested fix, and a priority level (high, medium, low)."
            ),
            expected_output=(
                "JSON array of fixes: [{\"violation\": \"...\", \"fix\": \"...\", "
                "\"priority\": \"high\"}]"
            ),
            agent=self.fix_agent,
            context=[task_compliance],
        )

        task_risk = Task(
            description=(
                "Compute the overall compliance risk score using all agent outputs. "
                "Visual violations weight = 40%, audio = 30%, policy = 30%. "
                "Call the compute_risk_score tool with all outputs. "
                "Return overall_score (0-100) and risk_level (low, medium, high, critical)."
            ),
            expected_output=(
                "JSON object: {\"overall_score\": 72.5, \"risk_level\": \"medium\", "
                "\"breakdown\": {...}}"
            ),
            agent=self.risk_agent,
            context=[task_vision, task_audio, task_compliance, task_fix],
        )

        return [task_vision, task_audio, task_compliance, task_fix, task_risk]

    def run(self, frames: list[str], audio_path: str, scan_id: str) -> dict:
        """Execute the compliance scanning crew and return structured results."""
        tasks = self.create_tasks(frames, audio_path, scan_id)

        crew = Crew(
            agents=[
                self.vision_agent,
                self.audio_agent,
                self.compliance_agent,
                self.fix_agent,
                self.risk_agent,
            ],
            tasks=tasks,
            verbose=True,
        )

        result = crew.kickoff()
        logger.info("Crew execution completed for scan %s", scan_id)

        # Parse outputs from each task
        outputs = {task.description.split(".")[0][:30]: task.output for task in tasks}

        # Build ScanResponse-compatible dict
        # Attempt to parse risk score JSON
        risk_data = {"overall_score": 50.0, "risk_level": "medium", "breakdown": {}}
        try:
            risk_task_output = tasks[-1].output or "{}"
            parsed = json.loads(risk_task_output)
            if isinstance(parsed, dict):
                risk_data = parsed
        except (json.JSONDecodeError, TypeError):
            logger.warning("Could not parse risk task output as JSON")

        # Attempt to parse compliance violations
        violations: list[dict] = []
        try:
            compliance_output = tasks[2].output or "[]"
            parsed = json.loads(compliance_output)
            if isinstance(parsed, list):
                violations = parsed
            elif isinstance(parsed, dict) and "violations" in parsed:
                violations = parsed["violations"]
        except (json.JSONDecodeError, TypeError):
            logger.warning("Could not parse compliance task output as JSON")

        # Attempt to parse fixes
        fixes: list[dict] = []
        try:
            fix_output = tasks[3].output or "[]"
            parsed = json.loads(fix_output)
            if isinstance(parsed, list):
                fixes = parsed
            elif isinstance(parsed, dict) and "fixes" in parsed:
                fixes = parsed["fixes"]
        except (json.JSONDecodeError, TypeError):
            logger.warning("Could not parse fix task output as JSON")

        summary = (
            f"Scan completed with {len(violations)} violations detected. "
            f"Risk level: {risk_data.get('risk_level', 'unknown')}. "
            f"Overall score: {risk_data.get('overall_score', 0)}."
        )

        return {
            "scan_id": scan_id,
            "status": "completed",
            "platform": self.platform,
            "risk_level": risk_data.get("risk_level", "medium"),
            "overall_score": float(risk_data.get("overall_score", 0)),
            "violations": violations,
            "fixes": fixes,
            "summary": summary,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
        }
