import logging
from abc import ABC, abstractmethod
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.notification import Notification
from .models import NotificationRequest, NotificationResult, NotificationStatus

logger = logging.getLogger("sangrahalayamu.notifications.providers")


class NotificationProvider(ABC):
    """
    Abstract base class every notification provider must implement.
    Business services depend on this interface, never on concrete providers.
    """
    @abstractmethod
    def send(self, db: Session, request: NotificationRequest) -> NotificationResult:
        """Deliver the notification and return a structured result."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...


# ---------------------------------------------------------------------------
# In-App Provider — full implementation
# ---------------------------------------------------------------------------

class InAppProvider(NotificationProvider):
    """
    Persists the notification to the database table for in-app delivery.
    Lifecycle transition: PENDING → DELIVERED (stored for READ by the recipient).
    """
    @property
    def provider_name(self) -> str:
        return "in_app"

    def send(self, db: Session, request: NotificationRequest) -> NotificationResult:
        from app.services.notifications.repository import NotificationRepository

        # ------------------------------------------------------------------
        # Idempotency guard — skip insert if this key was already delivered
        # ------------------------------------------------------------------
        if request.idempotency_key:
            existing = NotificationRepository.find_by_idempotency_key(
                db, request.idempotency_key
            )
            if existing is not None:
                logger.info(
                    f"[InAppProvider] Duplicate suppressed — idempotency_key "
                    f"'{request.idempotency_key}' already delivered "
                    f"(notification_id={existing.notification_id})"
                )
                return NotificationResult(
                    success=True,
                    provider=self.provider_name,
                    delivery_status=NotificationStatus.DUPLICATE,
                    sent_at=existing.created_at,
                    is_duplicate=True,
                )

        # ------------------------------------------------------------------
        # First-time delivery — persist the notification record
        # ------------------------------------------------------------------
        try:
            record = Notification(
                notification_id=request.notification_id,
                idempotency_key=request.idempotency_key,
                recipient_id=request.recipient_id,
                event_type=request.event_type,
                channel="in_app",
                priority=request.priority,
                title=request.title,
                message=request.message,
                metadata_json=request.metadata,
                is_read=False,
                delivery_status=NotificationStatus.DELIVERED.value,
                created_at=request.created_at,
            )
            db.add(record)
            db.commit()
            db.refresh(record)

            logger.info(
                f"[InAppProvider] Notification '{request.notification_id}' delivered "
                f"to recipient #{request.recipient_id} | type={request.event_type} "
                f"| idempotency_key={request.idempotency_key}"
            )
            return NotificationResult(
                success=True,
                provider=self.provider_name,
                delivery_status=NotificationStatus.DELIVERED,
                sent_at=datetime.utcnow(),
            )
        except Exception as exc:
            db.rollback()
            logger.error(f"[InAppProvider] Delivery failed: {exc}")
            return NotificationResult(
                success=False,
                provider=self.provider_name,
                delivery_status=NotificationStatus.FAILED,
                sent_at=datetime.utcnow(),
                error_message=str(exc),
            )


# ---------------------------------------------------------------------------
# Stub providers — ready for future configuration
# ---------------------------------------------------------------------------

class EmailProvider(NotificationProvider):
    """Stub — SMTP / SES integration to be wired in a future ticket."""
    @property
    def provider_name(self) -> str:
        return "email"

    def send(self, db: Session, request: NotificationRequest) -> NotificationResult:
        logger.info(
            f"[EmailProvider] Stub: would send email to recipient #{request.recipient_id} "
            f"for event '{request.event_type}'"
        )
        return NotificationResult(
            success=True,
            provider=self.provider_name,
            delivery_status=NotificationStatus.DELIVERED,
            sent_at=datetime.utcnow(),
        )


class SlackProvider(NotificationProvider):
    """Stub — Slack Incoming Webhooks integration to be wired in a future ticket."""
    @property
    def provider_name(self) -> str:
        return "slack"

    def send(self, db: Session, request: NotificationRequest) -> NotificationResult:
        logger.info(
            f"[SlackProvider] Stub: would post Slack message to recipient #{request.recipient_id} "
            f"for event '{request.event_type}'"
        )
        return NotificationResult(
            success=True,
            provider=self.provider_name,
            delivery_status=NotificationStatus.DELIVERED,
            sent_at=datetime.utcnow(),
        )


class TeamsProvider(NotificationProvider):
    """Stub — Microsoft Teams connector to be wired in a future ticket."""
    @property
    def provider_name(self) -> str:
        return "teams"

    def send(self, db: Session, request: NotificationRequest) -> NotificationResult:
        logger.info(
            f"[TeamsProvider] Stub: would post Teams card to recipient #{request.recipient_id} "
            f"for event '{request.event_type}'"
        )
        return NotificationResult(
            success=True,
            provider=self.provider_name,
            delivery_status=NotificationStatus.DELIVERED,
            sent_at=datetime.utcnow(),
        )
