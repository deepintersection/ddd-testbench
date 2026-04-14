"""
Shared Kernel — value objects and types used across all bounded contexts.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone

# ─── Identifiers ───────────────────────────────────────────────


def generate_id() -> str:
    """
    Generate a UUID version 4 identifier string.

    Returns:
        A UUID v4 string (e.g., "3f8f9e2e-...").
    """
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """
    Get the current time in UTC.

    Returns:
        A timezone-aware datetime representing the current UTC time.
    """
    return datetime.now(timezone.utc)
