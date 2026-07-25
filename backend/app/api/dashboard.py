"""
Dashboard metrics and stats router for IndustryBrain-AI.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return dashboard summary stats."""
    total_docs = db.query(Document).count()
    total_audits = db.query(AuditLog).count()

    return {
        "status": "success",
        "data": {
            "total_documents": total_docs,
            "total_audit_events": total_audits,
            "user_email": current_user.email,
        },
    }
