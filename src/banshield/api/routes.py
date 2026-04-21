"""API routes for BanShield."""

import logging
import os
import shutil
import tempfile
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile

from banshield.api.models import ScanRequest, ScanResponse
from banshield.crew.compliance_crew import ComplianceCrew
from banshield.policies.updater import update_policies
from banshield.services.video_processor import VideoProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory cache for scan results
_scan_results: dict[str, dict] = {}

_ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"}
_MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB


@router.post("/scan", response_model=ScanResponse)
async def scan_video(
    file: UploadFile = File(...), platform: str = "both"
) -> ScanResponse:
    """Upload and scan a video ad for compliance issues."""
    if file.content_type not in _ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed: mp4, mov, avi, webm.",
        )

    temp_dir = tempfile.mkdtemp(prefix="banshield_scan_")
    temp_path = os.path.join(temp_dir, file.filename or "video.mp4")

    try:
        with open(temp_path, "wb") as f:
            while chunk := await file.read(8192):
                f.write(chunk)

        file_size = os.path.getsize(temp_path)
        if file_size > _MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {file_size} bytes. Max: {_MAX_FILE_SIZE_BYTES}.",
            )

        logger.info("Processing uploaded video: %s (%d bytes)", temp_path, file_size)
        processor = VideoProcessor()
        processed = await processor.process(temp_path)

        crew = ComplianceCrew(platform=platform)
        result = crew.run(
            frames=processed["frames"],
            audio_path=processed["audio_path"],
            scan_id=processed["scan_id"],
        )
        _scan_results[result["scan_id"]] = result
        return ScanResponse(**result)

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Scan failed for uploaded file")
        raise HTTPException(status_code=500, detail=f"Scan failed: {exc}") from exc
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@router.post("/scan/url", response_model=ScanResponse)
async def scan_video_url(request: ScanRequest) -> ScanResponse:
    """Scan a video ad from a URL for compliance issues."""
    url = str(request.url)
    temp_dir = tempfile.mkdtemp(prefix="banshield_scan_")
    temp_path = os.path.join(temp_dir, "video.mp4")

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=120.0) as client:
            response = await client.get(url)
            response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if not any(ct in content_type for ct in _ALLOWED_VIDEO_TYPES):
            logger.warning("URL content-type may not be video: %s", content_type)

        file_size = len(response.content)
        if file_size > _MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Downloaded file too large: {file_size} bytes. Max: {_MAX_FILE_SIZE_BYTES}.",
            )

        with open(temp_path, "wb") as f:
            f.write(response.content)

        logger.info("Processing video from URL: %s (%d bytes)", url, file_size)
        processor = VideoProcessor()
        processed = await processor.process(temp_path)

        crew = ComplianceCrew(platform=request.platform)
        result = crew.run(
            frames=processed["frames"],
            audio_path=processed["audio_path"],
            scan_id=processed["scan_id"],
        )
        _scan_results[result["scan_id"]] = result
        return ScanResponse(**result)

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Scan failed for URL: %s", url)
        raise HTTPException(status_code=500, detail=f"Scan failed: {exc}") from exc
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@router.get("/scan/{scan_id}", response_model=ScanResponse)
async def get_scan_result(scan_id: str) -> ScanResponse:
    """Return cached scan result by scan_id."""
    if scan_id not in _scan_results:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")
    return ScanResponse(**_scan_results[scan_id])


@router.post("/policies/update")
async def trigger_policy_update() -> dict[str, str]:
    """Trigger a manual policy update."""
    # Fire-and-forget background task
    import asyncio

    asyncio.create_task(_run_policy_update())
    return {"status": "started", "message": "Policy update triggered"}


async def _run_policy_update() -> None:
    """Run policy update in background."""
    try:
        await update_policies()
    except Exception:
        logger.exception("Background policy update failed")


@router.get("/policies/status")
async def policy_status() -> dict:
    """Return last update timestamp and chunk count from Qdrant."""
    from banshield.policies.embedder import PolicyEmbedder

    embedder = PolicyEmbedder()
    try:
        info = embedder.qdrant.get_collection(embedder.collection_name)
        points_count = info.points_count
    except Exception:
        points_count = 0

    # Attempt to read last update time from a simple file marker
    marker_path = os.path.join("data", ".last_policy_update")
    last_update = None
    if os.path.exists(marker_path):
        with open(marker_path) as f:
            last_update = f.read().strip()

    return {
        "collection": embedder.collection_name,
        "chunks_stored": points_count,
        "last_update": last_update,
    }


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
