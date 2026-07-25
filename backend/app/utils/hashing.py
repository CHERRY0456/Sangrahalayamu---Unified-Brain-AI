"""
Cryptographic hashing utility functions for IndustryBrain-AI.
"""
import hashlib
from typing import Union


def calculate_sha256(content: Union[str, bytes]) -> str:
    """Calculate SHA-256 hash of string or byte input."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def calculate_md5(content: Union[str, bytes]) -> str:
    """Calculate MD5 checksum of string or byte input."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.md5(content).hexdigest()
