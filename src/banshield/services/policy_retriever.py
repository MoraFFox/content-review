"""RAG policy retrieval from Qdrant using Azure embeddings."""

import logging

from openai import AsyncAzureOpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from banshield.config import settings

logger = logging.getLogger(__name__)


class PolicyRetriever:
    """Retrieves relevant policy chunks from Qdrant via vector search."""

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

    async def retrieve(self, query: str, platform: str, top_k: int = 5) -> list[str]:
        """Embed query and return top-K policy chunks for the platform."""
        response = await self.openai.embeddings.create(
            input=[query],
            model=settings.azure_embedding_deployment,
        )
        query_vector = response.data[0].embedding

        search_result = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="platform",
                        match=MatchValue(value=platform),
                    )
                ]
            ),
        )

        chunks = [hit.payload["chunk"] for hit in search_result if hit.payload]
        logger.info("Retrieved %d policy chunks for platform '%s'", len(chunks), platform)
        return chunks
