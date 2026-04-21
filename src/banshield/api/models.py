"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, HttpUrl


class ViolationDetail(BaseModel):
    """A single compliance violation found in the video."""

    category: str  # "visual" | "audio" | "policy"
    description: str
    timestamp: float | None = None  # video timestamp in seconds if applicable
    severity: str  # "low" | "medium" | "high"
    policy_reference: str | None = None  # actual policy rule it violates


class FixSuggestion(BaseModel):
    """A suggested fix for a compliance violation."""

    violation: str
    fix: str
    priority: str  # "low" | "medium" | "high"


class ScanResponse(BaseModel):
    """Response model for scan results."""

    scan_id: str
    status: str  # "completed" | "failed" | "processing"
    platform: str  # "meta" | "tiktok" | "both"
    risk_level: str  # "low" | "medium" | "high" | "critical"
    overall_score: float  # 0-100
    violations: list[ViolationDetail]
    fixes: list[FixSuggestion]
    summary: str
    scanned_at: str  # ISO timestamp


class ScanRequest(BaseModel):
    """Request model for scanning a video by URL."""

    url: HttpUrl
    platform: str = "both"  # "meta" | "tiktok" | "both"
