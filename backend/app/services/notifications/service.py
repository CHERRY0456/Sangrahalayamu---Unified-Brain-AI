"""
Notification Service — Ticket #12
===================================
Single-entry orchestrator that:
  1. Validates global kill-switch (ENABLE_NOTIFICATIONS).
  2. Evaluates per-user preferences (channel, priority threshold, enabled flag).
  3. Formats title + message via NotificationFormatter (template substitution).
  4. Delegates delivery to the configured NotificationProvider.
  5. Returns a structured NotificationResult carrying the lifecycle status.

Business services (Access Control, Upload, Processing, Audit) publish a
NotificationRequest and receive a NotificationResult without knowing the
active delivery channel.
"""
import logging
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification import Notification
from .models import NotificationRequest, NotificationResult, NotificationStatus
from .formatter import NotificationFormatter
from .preferences import PreferenceEvaluator
from .provider_factory import NotificationProviderFactory
from .repository import NotificationRepository

logger = logging.getLogger("sangrahalayamu.notifications.service")


class NotificationService:
    """
    Provider-agnostic notification orchestrator.
    """

    def send_notification(
        self,
        db: Session,
        request: NotificationRequest,
    ) -> NotificationResult:
        """
        Send a notification through the configured provider.

        Lifecycle:  caller publishes NotificationRequest
                    → preferences screened
                    → title/message formatted
                    → provider delivers (PENDING → DELIVERED or FAILED)
                    → recipient reads (DELIVERED → READ, triggered separately)
        """
        # 1. Global kill-switch
        if not settings.notifications.enable_notifications:
            logger.debug("[NotificationService] Notifications disabled globally. Skipping.")
            return NotificationResult(
                success=False,
                provider="none",
                delivery_status=NotificationStatus.FAILED,
                error_message="Notifications disabled by configuration.",
            )

        # 2. User preference screening
        permitted = PreferenceEvaluator.is_delivery_permitted(
            db, request.recipient_id, request.priority
        )
        if not permitted:
            logger.info(
                f"[NotificationService] Delivery skipped for recipient #{request.recipient_id} "
                f"— preference filter blocked priority '{request.priority}'."
            )
            return NotificationResult(
                success=False,
                provider="preferences",
                delivery_status=NotificationStatus.FAILED,
                error_message="Blocked by user preference (channel disabled or priority below threshold).",
            )

        # 3. Template formatting — inject metadata params into title/message
        formatted_title, formatted_message = NotificationFormatter.format_notification(
            request.event_type, request.metadata
        )
        # Override with formatted values only if the request used raw strings
        if request.title == request.event_type or not request.title:
            request.title = formatted_title
        if not request.message:
            request.message = formatted_message

        # 4. Resolve provider from configuration
        provider = NotificationProviderFactory.get_provider()

        # 5. Deliver
        result = provider.send(db, request)

        if result.success:
            logger.info(
                f"[NotificationService] '{request.event_type}' delivered via "
                f"'{provider.provider_name}' to recipient #{request.recipient_id} "
                f"| status={result.delivery_status.value}"
            )
        else:
            logger.warning(
                f"[NotificationService] Delivery FAILED for recipient #{request.recipient_id} "
                f"| error={result.error_message}"
            )

        return result

    # ------------------------------------------------------------------
    # Read / Acknowledge
    # ------------------------------------------------------------------

    def get_unread(self, db: Session, recipient_id: int) -> List[Notification]:
        return NotificationRepository.get_unread(db, recipient_id)

    def get_history(
        self, db: Session, recipient_id: int, limit: int = 50
    ) -> List[Notification]:
        return NotificationRepository.get_history(db, recipient_id, limit)

    def mark_as_read(
        self, db: Session, notification_id: str, recipient_id: int
    ) -> bool:
        return NotificationRepository.mark_as_read(db, notification_id, recipient_id)

    def mark_all_as_read(self, db: Session, recipient_id: int) -> int:
        return NotificationRepository.mark_all_as_read(db, recipient_id)

    def count_unread(self, db: Session, recipient_id: int) -> int:
        return NotificationRepository.count_unread(db, recipient_id)

    # ------------------------------------------------------------------
    # Preference management
    # ------------------------------------------------------------------

    def update_preferences(
        self,
        db: Session,
        user_id: int,
        enabled: Optional[bool] = None,
        preferred_channel: Optional[str] = None,
        minimum_priority: Optional[str] = None,
    ):
        return NotificationRepository.update_preference(
            db, user_id,
            enabled=enabled,
            preferred_channel=preferred_channel,
            minimum_priority=minimum_priority,
        )


# Module-level singleton
notification_service = NotificationService()
