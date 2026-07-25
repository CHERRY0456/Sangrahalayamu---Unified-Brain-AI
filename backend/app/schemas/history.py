"""
Conversation history Pydantic schemas.
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class HistoryItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conversation_id: str
    title: Optional[str] = None
    created_at: datetime
    message_count: int = 0


class HistoryListResponse(BaseModel):
    items: List[HistoryItemSchema]
    total: int
