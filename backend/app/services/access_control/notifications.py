"""
Access control notification dispatch handlers.
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session

logger = logging.getLogger("industrybrain.access_control.notifications")


def notify_access_request_status(
    db: Session,
    user_id: str,
    request_id: str,
    status: str,
    reason: Optional[str] = None
) -> None:
    """Send access request notification to user."""
    logger.info(f"Notification sent to user {user_id} for access request {request_id}: {status}")
