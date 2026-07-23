from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from .models import AuditEvent

class AuditLogRepository:
    """
    Immutable repository conducting append-only operations on the audit log database.
    (Ticket #11 constraints: never update or delete logs).
    """
    @staticmethod
    def append(db: Session, event: AuditEvent) -> AuditLog:
        # Check that ID does not exist already to ensure uniqueness
        existing = db.scalar(select(AuditLog).where(AuditLog.event_id == event.event_id))
        if existing:
            raise RuntimeError(f"Audit log constraint error: Event ID {event.event_id} already exists.")
            
        log = AuditLog(
            event_id=event.event_id,
            event_version=event.event_version,
            timestamp=event.timestamp,
            event_type=event.event_type,
            actor_id=event.actor_id,
            actor_role=event.actor_role,
            session_id=event.session_id,
            request_id=event.request_id,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            action=event.action,
            status=event.status,
            severity=event.severity,
            source_service=event.source_service,
            metadata_json=event.metadata
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def delete_record(db: Session, event_id: str):
        """
        Enforces immutable policy. Raises error if deletion is attempted.
        """
        raise NotImplementedError("Audit logs are immutable. Deletions are strictly prohibited.")

    @staticmethod
    def update_record(db: Session, event_id: str, updates: dict):
        """
        Enforces immutable policy. Raises error if update is attempted.
        """
        raise NotImplementedError("Audit logs are immutable. Updates are strictly prohibited.")

    @staticmethod
    def list_logs(
        db: Session,
        actor_id: Optional[int] = None,
        event_type: Optional[str] = None,
        request_id: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        stmt = select(AuditLog)
        
        if actor_id is not None:
            stmt = stmt.where(AuditLog.actor_id == actor_id)
        if event_type is not None:
            stmt = stmt.where(AuditLog.event_type == event_type)
        if request_id is not None:
            stmt = stmt.where(AuditLog.request_id == request_id)
        if severity is not None:
            stmt = stmt.where(AuditLog.severity == severity)
            
        stmt = stmt.order_by(AuditLog.timestamp.desc()).limit(limit)
        return list(db.scalars(stmt).all())
