"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from banshield.main import app


client = TestClient(app)


def test_health_check() -> None:
    """Test health endpoint returns healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
