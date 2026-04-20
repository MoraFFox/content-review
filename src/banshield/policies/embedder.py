"""Embedding generator and Qdrant storage for policy chunks."""

import logging

from openai import AsyncAzureOpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from banshield.config import settings

logger = logging.getLogger(__name__)


class PolicyEmbedder:
    """Generates embeddings for policy chunks and stores them in Qdrant."""

    def __init__(self) -> None:
        self.openai = AsyncAzureOpenAI(
            api_key=settings.azure_api_key,
            azure_endpoint=settings.azure_endpoint,
            api_version=settings.azure_api_version,
        )
        self.qdrant = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = "policies"
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create the policies collection if it does not exist."""
        collections = self.qdrant.get_collections().collections
        names = {c.name for c in collections}
        if self.collection_name not in names:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

    async def embed_and_store(self, chunks: list[dict]) -> None:
        """Embed policy chunks and upsert them into Qdrant."""
        if not chunks:
            logger.warning("No chunks provided to embed_and_store")
            return

        texts = [c["chunk"] for c in chunks]
        response = await self.openai.embeddings.create(
            input=texts,
            model=settings.azure_embedding_deployment,
        )
        embeddings = [item.embedding for item in response.data]

        points = [
            PointStruct(
                id=f"{chunk['platform']}:{chunk['url']}:{chunk['chunk_index']}",
                vector=embedding,
                payload={
                    "platform": chunk["platform"],
                    "url": chunk["url"],
                    "chunk": chunk["chunk"],
                    "chunk_index": chunk["chunk_index"],
                    "scraped_at": chunk["scraped_at"],
                },
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]

        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        logger.info("Stored %d policy chunks in Qdrant", len(points))
