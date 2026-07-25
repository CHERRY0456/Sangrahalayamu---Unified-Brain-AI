"""
Audit log Pydantic schemas.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class AuditLogBase(BaseModel):
    action: str
    resource: str
    details: Optional[Dict[str, Any]] = None


class AuditLogCreate(AuditLogBase):
    user_id: str


class AuditLogResponse(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    created_at: datetime
