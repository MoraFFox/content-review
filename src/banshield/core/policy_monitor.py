"""Policy change detection by comparing scraped text against stored Qdrant chunks."""

import logging
from datetime import datetime, timezone

from openai import AsyncAzureOpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from banshield.config import settings

logger = logging.getLogger(__name__)


class PolicyMonitor:
    """Detects changes in advertising policies by comparing new text to stored embeddings."""

    _SIMILARITY_THRESHOLD = 0.85

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

    async def check_for_changes(self, fresh_chunks: list[dict]) -> dict:
        """Compare fresh chunks against stored versions and flag changes.

        Args:
            fresh_chunks: List of dicts with keys: platform, url, chunk, chunk_index.

        Returns:
            Dict with changed (bool), changed_sections (list), last_checked (ISO timestamp).
        """
        # Ensure collection exists so we can query it
        collections = self.qdrant.get_collections().collections
        names = {c.name for c in collections}
        if self.collection_name not in names:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
            logger.info("Created policies collection for monitoring")
            return {
                "changed": False,
                "changed_sections": [],
                "last_checked": datetime.now(timezone.utc).isoformat(),
            }

        changed_sections: list[dict] = []

        for chunk in fresh_chunks:
            query = chunk["chunk"]
            platform = chunk["platform"]

            # Embed the fresh chunk text
            embed_response = await self.openai.embeddings.create(
                input=[query],
                model=settings.azure_embedding_deployment,
            )
            query_vector = embed_response.data[0].embedding

            # Search for the most similar stored chunk for this platform
            search_result = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=1,
                with_payload=True,
            )

            if not search_result:
                # Entirely new chunk — treat as changed
                changed_sections.append(
                    {
                        "platform": platform,
                        "url": chunk["url"],
                        "chunk_index": chunk["chunk_index"],
                        "reason": "new_chunk_no_match",
                        "similarity": 0.0,
                    }
                )
                continue

            best_match = search_result[0]
            similarity = best_match.score

            if similarity < self._SIMILARITY_THRESHOLD:
                changed_sections.append(
                    {
                        "platform": platform,
                        "url": chunk["url"],
                        "chunk_index": chunk["chunk_index"],
                        "reason": "similarity_below_threshold",
                        "similarity": round(similarity, 4),
                    }
                )

        return {
            "changed": bool(changed_sections),
            "changed_sections": changed_sections,
            "last_checked": datetime.now(timezone.utc).isoformat(),
        }
