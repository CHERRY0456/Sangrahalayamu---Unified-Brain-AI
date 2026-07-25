"""
Structured audit logger helper.
"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

logger = logging.getLogger("industrybrain.audit.logger")


def log_audit_event(
    db: Session,
    user_id: str,
    action: str,
    resource: str,
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """Persist an audit log entry in the RDBMS."""
    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        details=details or {}
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    logger.info(f"Audit log created for user {user_id}: {action} on {resource}")
    return audit_entry
