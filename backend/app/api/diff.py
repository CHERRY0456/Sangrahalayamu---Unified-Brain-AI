from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.processing.diff import doc_diff_engine

router = APIRouter(prefix="/documents", tags=["diff"])

class DocumentDiffRequest(BaseModel):
    document_id_a: int
    document_id_b: int

@router.post("/diff", response_model=dict)
def compare_document_versions(
    payload: DocumentDiffRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compares two document revisions clause-by-clause, generating additions (+),
    deletions (-), modifications (~), and similarity metrics.
    """
    return doc_diff_engine.compare_documents(
        db=db,
        doc_id_a=payload.document_id_a,
        doc_id_b=payload.document_id_b
    )
