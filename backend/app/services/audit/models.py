import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from .context import (
    get_ctx_actor_id,
    get_ctx_actor_role,
    get_ctx_session_id,
    get_ctx_request_id
)

class AuditEvent(BaseModel):
    """
    Standardized schema representing an auditable compliance interaction.
    Includes the 'event_version' field defaulting to '1.0' (Ticket #11 extension requirement).
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_version: str = Field(default="1.0", description="Audit event schema version for backward compatibility")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    actor_id: Optional[int] = Field(default_factory=get_ctx_actor_id)
    actor_role: Optional[str] = Field(default_factory=get_ctx_actor_role)
    session_id: Optional[str] = Field(default_factory=get_ctx_session_id)
    request_id: Optional[str] = Field(default_factory=get_ctx_request_id)
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: str
    status: str
    severity: str = "INFO"
    source_service: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class UserActivityEvent(BaseModel):
    """
    User-centric timeline item mapped from base audit events.
    """
    timestamp: datetime
    activity_description: str
    service: str
    status: str
    request_id: Optional[str] = None

class HistoryTimeline(BaseModel):
    """
    Container summarizing user activity history events.
    """
    user_id: int
    user_email: str
    events: List[UserActivityEvent] = Field(default_factory=list)
    summary: str
    statistics: Dict[str, Any] = Field(default_factory=dict)
