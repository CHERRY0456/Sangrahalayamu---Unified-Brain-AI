"""
Core logging setup and configuration for IndustryBrain-AI.
"""
import logging
import sys
from app.core.config import settings


def setup_logging(log_level: str = None) -> None:
    """Configure system-wide logging with structured output."""
    if log_level is None:
        log_level = getattr(settings, "LOG_LEVEL", "INFO")

    level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("neo4j").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


logger = logging.getLogger("industrybrain")
