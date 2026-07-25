"""
User response feedback SQLAlchemy model.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from datetime import datetime, timezone
import uuid
from app.database.base import Base


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    response_id = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 to 5 stars or thumbs up/down (-1, +1)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
