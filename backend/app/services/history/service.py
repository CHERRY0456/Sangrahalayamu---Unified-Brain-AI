"""
Conversation history management service.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.chat import Conversation, ChatMessage


class HistoryService:
    def get_user_conversations(self, db: Session, user_id: str, limit: int = 50) -> List[Conversation]:
        """Fetch conversations for a user ordered by recent activity."""
        return (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .all()
        )

    def get_conversation_messages(self, db: Session, conversation_id: str) -> List[ChatMessage]:
        """Fetch messages for a specific conversation."""
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )


history_service = HistoryService()
