from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.api.deps import get_current_user, PolicyUploadGuard
from app.schemas.upload import DocumentUploadResponse, DocumentListResponse
from app.services.upload import UploadService

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Receives document file content via multipart upload, validates MIME type,
    checks PolicyEngine ingestion permissions, writes to storage, and registers metadata.
    """
    # Read binary content
    file_content = await file.read()
    
    # Delegate to service layer
    doc = UploadService.upload_file(
        db=db,
        user=current_user,
        file_content=file_content,
        filename=file.filename,
        content_type=file.content_type
    )
    return doc

@router.get("/my", response_model=DocumentListResponse)
def list_my_uploads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists all active documents uploaded by the authenticated user.
    """
    documents = UploadService.list_user_uploads(db, current_user)
    return DocumentListResponse(documents=documents)

@router.get("/{document_id}", response_model=DocumentUploadResponse)
def get_document_metadata(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetches the metadata properties of the document, enforcing read clearance levels.
    """
    doc = UploadService.get_file_metadata(db, current_user, document_id)
    return doc

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivates document metadata and calls the StorageInterface to delete files.
    """
    UploadService.delete_file(db, current_user, document_id)
    return {"message": "Document metadata deactivated and asset removed from storage."}
