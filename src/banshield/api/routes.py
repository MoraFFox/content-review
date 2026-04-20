"""API routes for BanShield."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from banshield.api.models import ScanRequest, ScanResponse

router = APIRouter()


@router.post("/scan", response_model=ScanResponse)
async def scan_video(file: UploadFile = File(...)) -> ScanResponse:
    """Upload and scan a video ad for compliance issues."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/scan/url", response_model=ScanResponse)
async def scan_video_url(request: ScanRequest) -> ScanResponse:
    """Scan a video ad from a URL for compliance issues."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
