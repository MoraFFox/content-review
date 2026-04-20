"""Orchestrates policy scraping, embedding, and storage updates."""

import logging
from collections import Counter

from banshield.policies.embedder import PolicyEmbedder
from banshield.policies.scraper import PolicyScraper

logger = logging.getLogger(__name__)


async def update_policies() -> None:
    """Run the full pipeline: scrape all sources, embed, and store in Qdrant."""
    scraper = PolicyScraper()
    embedder = PolicyEmbedder()

    logger.info("Starting policy update pipeline")
    chunks = await scraper.scrape_all()
    await embedder.embed_and_store(chunks)

    counts = Counter(c["platform"] for c in chunks)
    for platform, count in counts.items():
        logger.info("Stored %d chunks for platform '%s'", count, platform)
