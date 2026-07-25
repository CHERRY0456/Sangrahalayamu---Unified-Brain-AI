"""
ID generation utilities for IndustryBrain-AI.
"""
import uuid


def generate_uuid() -> str:
    """Generate a standard UUID4 string."""
    return str(uuid.uuid4())


def generate_short_id(prefix: str = "id") -> str:
    """Generate a short unique identifier with optional prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"
