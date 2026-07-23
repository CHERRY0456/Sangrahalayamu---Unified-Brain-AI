from datetime import datetime
from typing import Optional, Any
from sqlalchemy import select
from app.models.audit_log import AuditLog

class AuditFilterBuilder:
    @staticmethod
    def build_query(
        actor_id: Optional[int] = None,
        event_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        source_service: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Any:
        """
        Builds filter statements dynamically matching search variables (Ticket #11 constraint).
        """
        stmt = select(AuditLog)

        if actor_id is not None:
            stmt = stmt.where(AuditLog.actor_id == actor_id)
        if event_type is not None:
            stmt = stmt.where(AuditLog.event_type == event_type)
        if resource_id is not None:
            stmt = stmt.where(AuditLog.resource_id == resource_id)
        if source_service is not None:
            stmt = stmt.where(AuditLog.source_service == source_service)
        if start_date is not None:
            stmt = stmt.where(AuditLog.timestamp >= start_date)
        if end_date is not None:
            stmt = stmt.where(AuditLog.timestamp <= end_date)
        if severity is not None:
            stmt = stmt.where(AuditLog.severity == severity)
        if status is not None:
            stmt = stmt.where(AuditLog.status == status)
        if request_id is not None:
            stmt = stmt.where(AuditLog.request_id == request_id)

        stmt = stmt.order_by(AuditLog.timestamp.desc())
        return stmt
