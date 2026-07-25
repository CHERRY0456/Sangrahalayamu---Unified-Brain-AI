"""
File and path utility functions for IndustryBrain-AI.
"""
import os
import re
from typing import Tuple


def get_file_extension(filename: str) -> str:
    """Extract lowercase file extension without leading dot."""
    _, ext = os.path.splitext(filename)
    return ext.lstrip(".").lower()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing dangerous path characters and whitespace."""
    filename = os.path.basename(filename)
    filename = re.sub(r"[^\w\.-]", "_", filename)
    return filename.strip()


def get_file_size_mb(file_path: str) -> float:
    """Return file size in Megabytes."""
    if not os.path.exists(file_path):
        return 0.0
    return os.path.getsize(file_path) / (1024 * 1024)
