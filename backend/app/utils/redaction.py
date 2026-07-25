"""
PII and sensitive data redaction utilities for IndustryBrain-AI.
"""
import re

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
API_KEY_PATTERN = re.compile(r"(?:api[_-]?key|secret|password)\s*[:=]\s*['\"]?([^\s'\"]+)", re.IGNORECASE)


def redact_pii(text: str) -> str:
    """Redact sensitive PII patterns like email addresses."""
    if not text:
        return ""
    return EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)


def redact_secrets(text: str) -> str:
    """Redact API keys, tokens, and passwords in text strings."""
    if not text:
        return ""
    return API_KEY_PATTERN.sub(r"\1: [REDACTED_SECRET]", text)
