"""Orchestrates policy scraping, embedding, and storage updates."""

import logging
import os
from collections import Counter
from datetime import datetime, timezone

from banshield.core.policy_monitor import PolicyMonitor
from banshield.policies.embedder import PolicyEmbedder
from banshield.policies.scraper import PolicyScraper

logger = logging.getLogger(__name__)


async def update_policies() -> dict:
    """Run the full pipeline: scrape, monitor for changes, embed, and store in Qdrant."""
    scraper = PolicyScraper()
    monitor = PolicyMonitor()
    embedder = PolicyEmbedder()

    logger.info("Starting policy update pipeline")
    chunks = await scraper.scrape_all()

    # Check for changes before overwriting
    change_report = await monitor.check_for_changes(chunks)
    if change_report["changed"]:
        logger.warning(
            "Policy changes detected in %d sections",
            len(change_report["changed_sections"]),
        )
        for section in change_report["changed_sections"]:
            logger.warning(
                "Changed: %s chunk %d on %s (similarity: %s, reason: %s)",
                section["url"],
                section["chunk_index"],
                section["platform"],
                section.get("similarity", "N/A"),
                section["reason"],
            )

    # Store new chunks regardless (upsert handles duplicates)
    await embedder.embed_and_store(chunks)

    counts = Counter(c["platform"] for c in chunks)
    for platform, count in counts.items():
        logger.info("Stored %d chunks for platform '%s'", count, platform)

    # Write last-update marker
    os.makedirs("data", exist_ok=True)
    marker_path = os.path.join("data", ".last_policy_update")
    with open(marker_path, "w") as f:
        f.write(datetime.now(timezone.utc).isoformat())

    return {
        "chunks_stored": len(chunks),
        "changes_detected": change_report["changed"],
        "changed_sections": change_report["changed_sections"],
    }
