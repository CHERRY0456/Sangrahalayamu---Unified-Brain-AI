import hashlib
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator


class NotificationStatus(str, Enum):
    """
    Standardized notification status lifecycle states (Ticket #12 constraint).
    PENDING -> DELIVERED -> READ  (or FAILED on provider error / idempotency skip).
    """
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    READ = "READ"
    FAILED = "FAILED"
    # Returned when an existing notification with the same idempotency_key is found —
    # operation was a no-op, the original delivery remains in effect.
    DUPLICATE = "DUPLICATE"


class NotificationRequest(BaseModel):
    """
    Standardized notification delivery request schema.

    idempotency_key
    ---------------
    Callers may supply an explicit key (e.g. a deterministic UUID derived from
    their workflow ID).  If omitted, the service derives one automatically from
    the SHA-256 hash of  request_id + event_type + recipient_id.  This guarantees
    that retrying the same logical event never produces duplicate in-app records,
    surviving service restarts or repeated event publishes.
    """
    notification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    recipient_id: int
    recipient_role: Optional[str] = None
    channel: str = "in_app"
    priority: str = "INFO"
    title: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Idempotency key — caller-supplied or auto-derived after model construction
    idempotency_key: Optional[str] = None

    @model_validator(mode="after")
    def _derive_idempotency_key(self) -> "NotificationRequest":
        """
        Auto-derive the idempotency_key from request_id + event_type + recipient_id
        when the caller has not provided one explicitly.  The key is a truncated
        SHA-256 hex digest (first 40 chars) making it compact yet collision-resistant.
        """
        if not self.idempotency_key:
            raw = f"{self.request_id or self.notification_id}:{self.event_type}:{self.recipient_id}"
            self.idempotency_key = hashlib.sha256(raw.encode()).hexdigest()[:40]
        return self


class NotificationResult(BaseModel):
    """
    Delivery feedback returned by providers.
    """
    success: bool
    provider: str
    delivery_status: NotificationStatus
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    # True when a prior delivery with the same idempotency_key was found —
    # the original record was returned unchanged; no new row was inserted.
    is_duplicate: bool = False
