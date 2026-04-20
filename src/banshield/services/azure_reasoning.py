"""Azure OpenAI service for reasoning and compliance evaluation."""

from openai import AsyncAzureOpenAI
from banshield.config import settings


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
        raise NotImplementedError
