"""Azure AI Vision service for frame analysis."""

from banshield.config import settings


class AzureVisionService:
    """Service for analyzing video frames using Azure AI Vision."""

    def __init__(self) -> None:
        self.endpoint = settings.azure_vision_endpoint
        self.key = settings.azure_vision_key

    async def analyze_frame(self, frame_path: str) -> dict:
        """Analyze a single video frame."""
        raise NotImplementedError
