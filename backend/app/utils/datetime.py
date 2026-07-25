"""
Datetime utility functions for IndustryBrain-AI.
"""
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    """Return the current datetime in UTC timezone."""
    return datetime.now(timezone.utc)


def format_iso(dt: Optional[datetime] = None) -> str:
    """Format a datetime object as an ISO-8601 string."""
    if dt is None:
        dt = utc_now()
    return dt.isoformat()


def parse_iso(iso_str: str) -> datetime:
    """Parse an ISO-8601 string into a datetime object."""
    return datetime.fromisoformat(iso_str)
