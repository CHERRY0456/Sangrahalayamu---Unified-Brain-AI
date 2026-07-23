import json
import uuid
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from app.core.config import settings
from .schemas.memory import Conversation, ConversationMessage

class BaseConversationManager(ABC):
    """
    Interface for conversation memory storage.
    """
    @abstractmethod
    def get_conversation_history(self, db: Session, conversation_id: str, user_id: int, workspace_id: str, limit: int = 10) -> List[Dict[str, str]]:
        pass
        
    @abstractmethod
    def add_message(self, db: Session, conversation_id: str, user_id: int, workspace_id: str, role: str, content: str, metadata: dict = None):
        pass

    @abstractmethod
    def list_conversations(self, db: Session, user_id: int, workspace_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete_conversation(self, db: Session, conversation_id: str, user_id: int, workspace_id: str):
        pass

    @abstractmethod
    def get_conversation_messages(self, db: Session, conversation_id: str, user_id: int, workspace_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_message(self, db: Session, message_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        pass

class PostgresConversationManager(BaseConversationManager):
    """
    PostgreSQL-backed conversation manager using raw SQL / text for generic table insertion,
    allowing easy swap to Redis later without changing consumers.
    Expects a `conversations` table or handles it gracefully.
    """
    def __init__(self):
        self._ensure_table_exists_query = text("""
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id UUID PRIMARY KEY,
                conversation_id UUID NOT NULL,
                user_id INTEGER NOT NULL,
                workspace_id VARCHAR NOT NULL,
                role VARCHAR(10) NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_conv_msg ON conversation_messages(conversation_id, created_at);
        """)
        self._table_checked = False

    def _check_table(self, db: Session):
        if not self._table_checked:
            db.execute(self._ensure_table_exists_query)
            db.commit()
            self._table_checked = True

    def get_conversation_history(self, db: Session, conversation_id: str, user_id: int, workspace_id: str, limit: int = 10) -> List[Dict[str, str]]:
        self._check_table(db)
        
        # We only retrieve messages for the explicit user/workspace to prevent data leakage
        query = text("""
            SELECT role, content 
            FROM conversation_messages
            WHERE conversation_id = :conv_id 
              AND user_id = :user_id 
              AND workspace_id = :workspace_id
            ORDER BY created_at DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {
            "conv_id": conversation_id,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "limit": limit
        }).fetchall()
        
        # Result is ordered by DESC (newest first). We need to return it in chronological order.
        history = [{"role": row[0], "content": row[1]} for row in result]
        history.reverse()
        return history

    def add_message(self, db: Session, conversation_id: str, user_id: int, workspace_id: str, role: str, content: str, metadata: dict = None):
        self._check_table(db)
        
        query = text("""
            INSERT INTO conversation_messages (id, conversation_id, user_id, workspace_id, role, content, metadata, created_at)
            VALUES (:id, :conv_id, :user_id, :workspace_id, :role, :content, :metadata, :created_at)
        """)
        
        db.execute(query, {
            "id": str(uuid.uuid4()),
            "conv_id": conversation_id,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "role": role,
            "content": content,
            "metadata": json.dumps(metadata) if metadata else "{}",
            "created_at": datetime.utcnow()
        })
        db.commit()

    def list_conversations(self, db: Session, user_id: int, workspace_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        self._check_table(db)
        # Query unique conversations for the user/workspace, ordered by the latest message time
        query = text("""
            WITH convs AS (
                SELECT conversation_id, MAX(created_at) as last_activity, COUNT(*) as msg_count
                FROM conversation_messages
                WHERE user_id = :user_id AND workspace_id = :workspace_id
                GROUP BY conversation_id
            ),
            first_msgs AS (
                SELECT DISTINCT ON (conversation_id) conversation_id, content
                FROM conversation_messages
                WHERE user_id = :user_id AND workspace_id = :workspace_id AND role = 'user'
                ORDER BY conversation_id, created_at ASC
            )
            SELECT c.conversation_id, c.last_activity, c.msg_count, COALESCE(f.content, 'New Chat Session') as first_msg
            FROM convs c
            LEFT JOIN first_msgs f ON f.conversation_id = c.conversation_id
            ORDER BY c.last_activity DESC
            LIMIT :limit
        """)
        result = db.execute(query, {
            "user_id": user_id,
            "workspace_id": workspace_id,
            "limit": limit
        }).fetchall()
        
        conversations = []
        for row in result:
            conv_id = str(row[0])
            last_activity = row[1]
            msg_count = row[2]
            first_msg = row[3]
            # Derive title: first 40 chars of first message
            title = first_msg[:40] + "..." if len(first_msg) > 40 else first_msg
            conversations.append({
                "id": conv_id,
                "title": title,
                "updatedAt": last_activity.isoformat() if last_activity else None,
                "responsesCount": msg_count
            })
        return conversations

    def delete_conversation(self, db: Session, conversation_id: str, user_id: int, workspace_id: str):
        self._check_table(db)
        query = text("""
            DELETE FROM conversation_messages
            WHERE conversation_id = :conv_id AND user_id = :user_id AND workspace_id = :workspace_id
        """)
        db.execute(query, {
            "conv_id": conversation_id,
            "user_id": user_id,
            "workspace_id": workspace_id
        })
        db.commit()

    def get_conversation_messages(self, db: Session, conversation_id: str, user_id: int, workspace_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        self._check_table(db)
        query = text("""
            SELECT id, role, content, metadata, created_at
            FROM conversation_messages
            WHERE conversation_id = :conv_id 
              AND user_id = :user_id 
              AND workspace_id = :workspace_id
            ORDER BY created_at ASC
            LIMIT :limit
        """)
        result = db.execute(query, {
            "conv_id": conversation_id,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "limit": limit
        }).fetchall()
        
        messages = []
        for row in result:
            msg_id = str(row[0])
            role = row[1]
            content = row[2]
            meta = row[3]
            created_at = row[4]
            
            # If metadata is string, parse it
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except:
                    meta = {}
            
            # Map role to sender
            sender = 'user' if role == 'user' else 'ai'
            
            messages.append({
                "id": msg_id,
                "sender": sender,
                "text": content,
                "timestamp": created_at.strftime("%I:%M %p") if created_at else "",
                "metadata": meta
            })
        return messages

    def get_message(self, db: Session, message_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        self._check_table(db)
        query = text("""
            SELECT id, role, content, metadata, created_at, conversation_id, workspace_id
            FROM conversation_messages
            WHERE id = :msg_id AND user_id = :user_id
        """)
        row = db.execute(query, {"msg_id": message_id, "user_id": user_id}).fetchone()
        if not row:
            return None
        
        meta = row[3]
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except:
                meta = {}
                
        return {
            "id": str(row[0]),
            "role": row[1],
            "content": row[2],
            "metadata": meta,
            "created_at": row[4],
            "conversation_id": str(row[5]),
            "workspace_id": row[6]
        }

# Export singleton matching the interface
conversation_manager: BaseConversationManager = PostgresConversationManager()
