import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from .models import AuditEvent
from .events import DBAuditPublisher
from .repository import AuditLogRepository

logger = logging.getLogger("sangrahalayamu.audit.service")

class AuditService:
    """
    Central Audit service coordinating compliance recording and event sinks.
    Acts as an append-only event consumer (sinks only, decoupled from workflows) (Ticket #11 constraints).
    """
    def __init__(self):
        # Default direct database publisher
        self.publisher = DBAuditPublisher()

    def record_event(self, db: Session, event: AuditEvent) -> None:
        """
        Consumes audit events and publishes them securely to the append-only logs database index.
        """
        if not settings.audit.enable_audit_logging:
            return

        try:
            # Emits event to active publisher sink (direct db writer)
            self.publisher.publish(db, event)
            logger.debug(f"Audit log successfully registered. Event: {event.event_id} | Type: {event.event_type}")
        except Exception as e:
            logger.error(f"Audit log registration failed: {str(e)}")

# Global singleton instance for platform pings
audit_service = AuditService()
