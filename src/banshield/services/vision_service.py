"""Azure OpenAI vision analysis for video frames."""

import base64
import logging

from openai import AsyncAzureOpenAI

from banshield.config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an expert advertising compliance analyst. Analyze the provided video frames "
    "and identify any of the following issues: explicit or adult content, misleading or "
    "false claims, prohibited products (weapons, drugs, tobacco, etc.), problematic text "
    "overlays, and brand safety concerns. Return your findings as a concise JSON array of "
    'issues. Each issue must include: "issue_type", "description", and "severity" '
    '(low, medium, high). If no issues are found, return an empty array. Frame your '
    "response ONLY as valid JSON with no markdown formatting."
)


class VisionService:
    """Analyzes video frames using Azure OpenAI GPT-4o vision."""

    def __init__(self) -> None:
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_api_key,
            azure_endpoint=settings.azure_endpoint,
            api_version=settings.azure_api_version,
        )

    @staticmethod
    def _encode_frame(frame_path: str) -> str:
        """Read a frame file and return a base64-encoded data URI."""
        with open(frame_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"

    async def _analyze_batch(self, batch: list[str]) -> list[dict]:
        """Analyze a batch of up to 5 frames."""
        images = [
            {
                "type": "image_url",
                "image_url": {"url": self._encode_frame(path), "detail": "auto"},
            }
            for path in batch
        ]

        response = await self.client.chat.completions.create(
            model="gpt-4o",  # vision-enabled deployment name
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": images},  # type: ignore[arg-type]
            ],
            max_tokens=2048,
            temperature=0.2,
        )

        content = response.choices[0].message.content or "[]"
        # Strip markdown code fences if present
        content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        import json

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            logger.warning("Vision response was not valid JSON: %s", content)
            parsed = []

        if not isinstance(parsed, list):
            parsed = [parsed] if parsed else []

        results = []
        for item in parsed:
            results.append(
                {
                    "frame_path": batch[0] if len(batch) == 1 else batch,
                    "issues": item if isinstance(item, list) else [item],
                }
            )
        return results

    async def analyze_frames(self, frame_paths: list[str]) -> list[dict]:
        """Analyze all frames in batches of 5 and return findings."""
        findings: list[dict] = []
        batch_size = 5

        for i in range(0, len(frame_paths), batch_size):
            batch = frame_paths[i : i + batch_size]
            logger.info("Analyzing vision batch %d-%d of %d", i + 1, i + len(batch), len(frame_paths))
            batch_results = await self._analyze_batch(batch)
            findings.extend(batch_results)

        return findings
