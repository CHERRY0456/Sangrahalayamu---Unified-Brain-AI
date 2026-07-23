import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from app.database.postgres import Base

class Notification(Base):
    """
    SQLAlchemy model representing a dispatched or pending user notification.
    Enforces the 'notification_status_lifecycle' using controlled status strings (Ticket #12 constraint).
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    notification_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    # Idempotency key prevents duplicate records on retries or repeated event publishes
    idempotency_key = Column(String(40), unique=True, index=True, nullable=True)
    recipient_id = Column(Integer, index=True, nullable=False)
    event_type = Column(String(50), nullable=False)
    channel = Column(String(20), nullable=False, default="in_app")
    priority = Column(String(20), nullable=False, default="INFO")
    title = Column(String(200), nullable=False)
    message = Column(String(500), nullable=False)
    metadata_json = Column(JSON, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    # Status lifecycle: PENDING -> DELIVERED -> READ (or FAILED)
    delivery_status = Column(String(20), default="PENDING", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    read_at = Column(DateTime, nullable=True)

class UserNotificationPreference(Base):
    """
    SQLAlchemy model storing user-specific channel and priority notification filters.
    """
    __tablename__ = "user_notification_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    preferred_channel = Column(String(20), default="in_app", nullable=False)
    minimum_priority = Column(String(20), default="INFO", nullable=False)
