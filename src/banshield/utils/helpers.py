"""Utility helpers for BanShield."""

import uuid


def generate_scan_id() -> str:
    """Generate a unique scan identifier."""
    return str(uuid.uuid4())
