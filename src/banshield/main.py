"""FastAPI application entry point for BanShield."""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from banshield.api.routes import router
from banshield.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: check if policies collection exists and has data
    try:
        from banshield.policies.embedder import PolicyEmbedder
        from banshield.policies.updater import update_policies

        embedder = PolicyEmbedder()
        collections = embedder.qdrant.get_collections().collections
        names = {c.name for c in collections}

        if embedder.collection_name not in names:
            logger.info("Policies collection not found. Triggering initial policy update...")
            import asyncio

            asyncio.create_task(_background_policy_update())
        else:
            info = embedder.qdrant.get_collection(embedder.collection_name)
            if info.points_count == 0:
                logger.info("Policies collection is empty. Triggering initial policy update...")
                import asyncio

                asyncio.create_task(_background_policy_update())
            else:
                logger.info(
                    "Policies collection ready with %d chunks", info.points_count
                )
    except Exception:
        logger.exception("Startup policy check failed")

    yield
    # Shutdown


async def _background_policy_update() -> None:
    """Run policy update in the background during startup."""
    try:
        from banshield.policies.updater import update_policies

        result = await update_policies()
        logger.info(
            "Background policy update complete: %d chunks stored, changes_detected=%s",
            result["chunks_stored"],
            result["changes_detected"],
        )
    except Exception:
        logger.exception("Background policy update failed")


app = FastAPI(
    title="BanShield",
    description="Video Ad Compliance Scanner API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1")


def main() -> None:
    """Run the application with uvicorn."""
    uvicorn.run(
        "banshield.main:app",
        host=settings.app_host,
        port=settings.app_port,
        log_level=settings.app_log_level,
        reload=True,
    )


if __name__ == "__main__":
    main()
