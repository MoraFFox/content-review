"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, HttpUrl


class ScanRequest(BaseModel):
    """Request model for scanning a video by URL."""

    url: HttpUrl
    compliance_rules: list[str] | None = None


class ScanResponse(BaseModel):
    """Response model for scan results."""

    scan_id: str
    status: str
    violations: list[dict]
    summary: str
    confidence_score: float
