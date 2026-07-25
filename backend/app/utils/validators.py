"""
Validation helper functions for IndustryBrain-AI.
"""
import re
from typing import List

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_email(email: str) -> bool:
    """Check if string is a valid email address."""
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Verify file extension is within allowed set."""
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    return ext in [e.lower().lstrip(".") for e in allowed_extensions]
