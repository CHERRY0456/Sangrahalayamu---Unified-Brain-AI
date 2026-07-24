import logging

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.upload import DocumentListResponse, DocumentUploadResponse
from app.services.processing.pipeline import DocumentProcessingPipeline
from app.services.upload import UploadService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])


def _to_document_response(doc) -> DocumentUploadResponse:
    return DocumentUploadResponse(
        id=doc.id,
        uuid=doc.uuid,
        name=doc.name,
        mime_type=doc.mime_type,
        file_size=doc.file_size,
        status=doc.status,
        classification=doc.classification,
        required_clearance=doc.required_clearance,
        department=doc.department,
        created_at=doc.created_at,
    )


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Stores an uploaded document, runs ingestion, and returns persisted status.
    """
    file_content = await file.read()
    doc = UploadService.upload_file(db, current_user, file_content, file.filename, file.content_type or "")

    try:
        DocumentProcessingPipeline.process_document(db, doc.id)
        db.refresh(doc)
    except Exception:
        db.refresh(doc)
        logger.exception("Document processing failed for document_id=%s", doc.id)
        return _to_document_response(doc)

    return _to_document_response(doc)


@router.get("", response_model=DocumentListResponse, status_code=status.HTTP_200_OK)
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns active documents uploaded by the authenticated user.
    """
    docs = UploadService.list_user_uploads(db, current_user)
    return DocumentListResponse(documents=[_to_document_response(doc) for doc in docs])
