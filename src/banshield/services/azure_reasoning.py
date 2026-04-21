"""Azure OpenAI service for reasoning and compliance evaluation."""

import json
import logging

from openai import AsyncAzureOpenAI

from banshield.config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an expert advertising compliance analyst. Analyze the provided "
    "transcript and identify any compliance violations based on the given rules. "
    "Return your findings as a JSON object with a 'violations' array. Each violation "
    'must include: "description", "severity" (low, medium, high), and "category". '
    "If no violations are found, return an empty violations array. "
    "Frame your response ONLY as valid JSON with no markdown formatting."
)


class AzureReasoningService:
    """Service for LLM-based reasoning using Azure OpenAI."""

    def __init__(self) -> None:
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_api_key,
            azure_endpoint=settings.azure_endpoint,
            api_version=settings.azure_api_version,
        )

    async def evaluate_compliance(self, content: str, rules: list[str]) -> dict:
        """Evaluate content against compliance rules."""
        rules_text = "\n".join(f"- {rule}" for rule in rules)
        user_prompt = (
            f"Rules to check:\n{rules_text}\n\n"
            f"Content to analyze:\n{content}\n\n"
            "Analyze the content against the rules and return a JSON object."
        )

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=2048,
            temperature=0.2,
        )

        content = response.choices[0].message.content or "{}"
        content = (
            content.strip()
            .removeprefix("```json")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            logger.warning("Reasoning response was not valid JSON: %s", content)
            parsed = {"violations": []}

        if not isinstance(parsed, dict):
            parsed = {"violations": []}

        return parsed
