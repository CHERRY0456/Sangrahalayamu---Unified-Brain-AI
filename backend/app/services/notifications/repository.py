import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.notification import Notification, UserNotificationPreference
from .models import NotificationStatus

logger = logging.getLogger("sangrahalayamu.notifications.repository")


class NotificationRepository:
    """
    Database persistence layer for notifications and user preferences.
    Notification records progress through the standardized status lifecycle:
    PENDING → DELIVERED → READ  (or FAILED on provider error).
    Idempotency checks prevent duplicate rows on retries.
    """

    # ------------------------------------------------------------------
    # Idempotency guard
    # ------------------------------------------------------------------

    @staticmethod
    def find_by_idempotency_key(
        db: Session,
        idempotency_key: str,
    ) -> Optional[Notification]:
        """
        Return an existing Notification whose idempotency_key matches,
        or None if this is a first-time delivery.
        """
        stmt = select(Notification).where(Notification.idempotency_key == idempotency_key)
        return db.scalar(stmt)

    # ------------------------------------------------------------------
    # Notification records
    # ------------------------------------------------------------------

    @staticmethod
    def get_unread(db: Session, recipient_id: int) -> List[Notification]:
        stmt = (
            select(Notification)
            .where(
                Notification.recipient_id == recipient_id,
                Notification.is_read == False,  # noqa: E712
            )
            .order_by(Notification.created_at.desc())
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_history(
        db: Session,
        recipient_id: int,
        limit: int = 50,
    ) -> List[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.recipient_id == recipient_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: str,
        recipient_id: int,
    ) -> bool:
        """
        Transitions status: DELIVERED → READ.
        Returns True if a matching unread record was updated.
        """
        stmt = (
            update(Notification)
            .where(
                Notification.notification_id == notification_id,
                Notification.recipient_id == recipient_id,
                Notification.is_read == False,  # noqa: E712
            )
            .values(
                is_read=True,
                read_at=datetime.utcnow(),
                delivery_status=NotificationStatus.READ.value,
            )
        )
        result = db.execute(stmt)
        db.commit()
        updated = result.rowcount > 0
        if updated:
            logger.info(
                f"[Repository] Notification '{notification_id}' marked READ "
                f"for recipient #{recipient_id}"
            )
        return updated

    @staticmethod
    def mark_all_as_read(db: Session, recipient_id: int) -> int:
        """
        Bulk lifecycle transition: DELIVERED → READ for all unread records.
        Returns the count of updated rows.
        """
        stmt = (
            update(Notification)
            .where(
                Notification.recipient_id == recipient_id,
                Notification.is_read == False,  # noqa: E712
            )
            .values(
                is_read=True,
                read_at=datetime.utcnow(),
                delivery_status=NotificationStatus.READ.value,
            )
        )
        result = db.execute(stmt)
        db.commit()
        count = result.rowcount
        logger.info(
            f"[Repository] {count} notifications marked READ for recipient #{recipient_id}"
        )
        return count

    @staticmethod
    def count_unread(db: Session, recipient_id: int) -> int:
        return len(NotificationRepository.get_unread(db, recipient_id))

    # ------------------------------------------------------------------
    # User preferences
    # ------------------------------------------------------------------

    @staticmethod
    def get_or_create_preference(
        db: Session,
        user_id: int,
    ) -> UserNotificationPreference:
        stmt = select(UserNotificationPreference).where(
            UserNotificationPreference.user_id == user_id
        )
        pref = db.scalar(stmt)
        if pref is None:
            pref = UserNotificationPreference(user_id=user_id)
            db.add(pref)
            db.commit()
            db.refresh(pref)
        return pref

    @staticmethod
    def update_preference(
        db: Session,
        user_id: int,
        enabled: Optional[bool] = None,
        preferred_channel: Optional[str] = None,
        minimum_priority: Optional[str] = None,
    ) -> UserNotificationPreference:
        pref = NotificationRepository.get_or_create_preference(db, user_id)
        if enabled is not None:
            pref.enabled = enabled
        if preferred_channel is not None:
            pref.preferred_channel = preferred_channel
        if minimum_priority is not None:
            pref.minimum_priority = minimum_priority
        db.commit()
        db.refresh(pref)
        return pref
