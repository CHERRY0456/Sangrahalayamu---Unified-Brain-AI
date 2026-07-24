from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.audit.repository import AuditLogRepository

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/events", status_code=status.HTTP_200_OK)
def get_audit_events(
    actor_id: Optional[int] = None,
    event_type: Optional[str] = None,
    request_id: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves compliance audit logs. Accessible by authorized authenticated users.
    """
    logs = AuditLogRepository.list_logs(
        db=db,
        actor_id=actor_id,
        event_type=event_type,
        request_id=request_id,
        severity=severity,
        limit=limit
    )
    
    # Map SQLAlchemy models to serialized dicts
    result = []
    for log in logs:
        # Format status
        db_status = log.status.upper()
        status_val = "Success"
        if "FAIL" in db_status:
            status_val = "Failed"
        elif "PEND" in db_status:
            status_val = "Pending"
        elif "WARN" in db_status:
            status_val = "Warning"
            
        # Format severity
        db_severity = log.severity.upper()
        severity_val = "Info"
        if "CRIT" in db_severity:
            severity_val = "Critical"
        elif "HIGH" in db_severity:
            severity_val = "High"
        elif "MED" in db_severity:
            severity_val = "Medium"
            
        meta = log.metadata_json or {}
        
        result.append({
            "id": log.event_id,
            "version": log.event_version,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "type": log.event_type,
            "user": f"User {log.actor_id}" if log.actor_id else "System",
            "actor_role": log.actor_role or "System",
            "session_id": log.session_id,
            "request_id": log.request_id,
            "action": log.action,
            "status": status_val,
            "severity": severity_val,
            "module": log.source_service,
            "relatedDoc": meta.get("document_name") or meta.get("file_name"),
            "relatedConvId": meta.get("conversation_id"),
            "notes": meta.get("notes") or f"Executed compliance audit for action: {log.action}.",
            "metadata": meta
        })
    return result

@router.get("/summary", status_code=status.HTTP_200_OK)
def get_audit_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves compliance audit summary metrics. Accessible by authorized authenticated users.
    """
    stats = AuditLogRepository.get_audit_summary_stats(db=db)
    return stats
