"""
Conversation history router for IndustryBrain-AI.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/conversations")
def list_user_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List recent conversation history for the current user."""
    return {
        "status": "success",
        "data": [],
        "user_id": str(current_user.id),
    }
