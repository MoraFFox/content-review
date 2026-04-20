"""Qdrant vector database service."""

from qdrant_client import QdrantClient
from banshield.config import settings


class QdrantService:
    """Service for vector storage and similarity search."""

    def __init__(self) -> None:
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key,
        )

    async def store_embedding(self, collection: str, vector: list[float], payload: dict) -> None:
        """Store a vector embedding with metadata."""
        raise NotImplementedError
