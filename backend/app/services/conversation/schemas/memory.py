from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class ConversationMessage(BaseModel):
    """
    Standardized conversation message schema.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str = Field(..., description="Role of the sender: 'user' or 'ai'")
    content: str = Field(..., description="The message content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata like citations or metrics")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Conversation(BaseModel):
    """
    Conversation holding multiple messages for a specific user and workspace.
    """
    id: str = Field(..., description="Conversation UUID")
    user_id: int = Field(..., description="ID of the user who owns the conversation")
    workspace_id: str = Field(..., description="Workspace ID where the conversation is taking place")
    messages: List[ConversationMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
