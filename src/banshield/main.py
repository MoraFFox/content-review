"""FastAPI application entry point for BanShield."""

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from banshield.api.routes import router
from banshield.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    yield
    # Shutdown


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
