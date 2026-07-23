import logging
from fastapi import APIRouter, Depends, File, UploadFile, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.upload import DocumentUploadResponse
from app.services.processing.pipeline import DocumentProcessingPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Receives document file content via multipart upload, validates MIME type,
    and runs the full Enterprise Ingestion Pipeline:
    Upload -> Parser Registry -> OCR -> Entities -> Relationships -> Semantic Chunking -> Embeddings -> Qdrant -> Neo4j.
    """
    file_content = await file.read()
    
    # Save document record placeholder to DB first (UploadService handles this typically)
    from app.services.upload import UploadService
    doc = UploadService.upload_file(db, current_user, file_content, file.filename, file.content_type)
    
    # Process pipeline (background tasks would be better, but we await for the test)
    # The DocumentProcessingPipeline expects a db and a document_id
    processed_doc = DocumentProcessingPipeline.process_document(db, doc.id)
    
    # Convert core Document model to response schema
    return DocumentUploadResponse(
        id=doc.id,
        name=doc.name,
        s3_url=doc.s3_url,
        doc_metadata=doc.doc_metadata,
        created_at=doc.created_at,
        is_active=doc.is_active
    )

from app.models.document import Document
from sqlalchemy import select
from app.schemas.upload import DocumentListResponse

@router.get("", response_model=DocumentListResponse, status_code=status.HTTP_200_OK)
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all active documents from the PostgreSQL database.
    """
    stmt = select(Document).where(Document.is_active == True)
    docs = db.scalars(stmt).all()
    return DocumentListResponse(documents=docs)
