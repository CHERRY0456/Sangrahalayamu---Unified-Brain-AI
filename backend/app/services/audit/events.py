from abc import ABC, abstractmethod
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from .models import AuditEvent

# Standardized event category constants (Ticket #11 constraint)
EVENT_TYPE_AUTHENTICATION = "Authentication"
EVENT_TYPE_AUTHORIZATION = "Authorization"
EVENT_TYPE_UPLOAD = "Upload"
EVENT_TYPE_STORAGE = "Storage"
EVENT_TYPE_PROCESSING = "Processing"
EVENT_TYPE_RETRIEVAL = "Retrieval"
EVENT_TYPE_AI_GENERATION = "AI Generation"
EVENT_TYPE_TRANSPARENCY = "Transparency"
EVENT_TYPE_RECOMMENDATION = "Recommendation"
EVENT_TYPE_ACCESS_OVERRIDE = "Access Override"
EVENT_TYPE_DOWNLOAD = "Download"
EVENT_TYPE_ADMINISTRATION = "Administration"
EVENT_TYPE_SYSTEM_HEALTH = "System Health"

class AuditPublisher(ABC):
    """
    Decoupled interface mapping event publishing.
    Allows easy swap of direct DB writes to message buses (Kafka, EventBridge, etc.).
    """
    @abstractmethod
    def publish(self, db: Session, event: AuditEvent) -> None:
        pass

class DBAuditPublisher(AuditPublisher):
    """
    Default Direct Database audit log writer.
    """
    def publish(self, db: Session, event: AuditEvent) -> None:
        log_entry = AuditLog(
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
        db.add(log_entry)
        db.commit()
