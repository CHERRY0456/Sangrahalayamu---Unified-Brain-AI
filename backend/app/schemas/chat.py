"""
Chat request and response Pydantic schemas.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatQueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    retrieval_filters: Optional[Dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: Optional[str]
    created_at: datetime
    messages: List[ChatMessageResponse] = []
