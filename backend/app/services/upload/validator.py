import os
import re
import hashlib
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.config import settings
from app.models.document import Document

class UploadValidator:
    ALLOWED_EXTENSIONS = {
        ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
        ".csv", ".tsv", ".txt", ".md", ".markdown", ".rtf", ".html",
        ".htm", ".xml", ".json", ".png", ".jpg", ".jpeg", ".webp",
        ".tiff", ".tif", ".eml", ".msg", ".log", ".err", ".out",
        ".py", ".js", ".ts", ".go", ".c", ".cpp", ".h", ".rs",
        ".java", ".sql", ".sh", ".cfg", ".conf", ".ini", ".svg",
        ".dwg", ".dxf"
    }
    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "text/csv",
        "text/tab-separated-values",
        "text/markdown",
        "text/html",
        "application/json",
        "application/xml",
        "text/xml",
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/tiff",
        "image/svg+xml",
        "message/rfc822",
        "application/octet-stream",
        ""
    }

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitizes the upload filename, retaining only safe alphanumeric characters, dots, and underscores.
        """
        base = os.path.basename(filename)
        # Substitute non-safe characters with underscores
        cleaned = re.sub(r"[^\w\.\-]", "_", base)
        return cleaned or "unnamed_file"

    @staticmethod
    def validate_file(db: Session, filename: str, content_type: str, file_content: bytes) -> str:
        """
        Runs format, size, mime, and pluggable duplication validation checks.
        Returns the sanitized filename string if validated.
        """
        # 1. Size verify (non-empty)
        file_size = len(file_content)
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploads are not accepted."
            )

        # 2. Maximum file size check
        if file_size > settings.processing.max_upload_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds the maximum limit of {settings.processing.max_upload_size} bytes."
            )

        # 3. Filename cleaning
        sanitized_name = UploadValidator.sanitize_filename(filename)
        file_ext = os.path.splitext(sanitized_name)[1].lower()

        # 4. Extension validation
        if file_ext not in UploadValidator.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension '{file_ext}'."
            )

        # 5. MIME type validation. Some browsers/OSes submit enterprise file
        # types as application/octet-stream, so extension + parser-registry
        # detection remains the primary source of truth.
        normalized_content_type = content_type or ""
        if normalized_content_type not in UploadValidator.ALLOWED_MIME_TYPES and not normalized_content_type.startswith(("text/", "image/")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"MIME type '{content_type}' is not supported for ingestion."
            )

        # 6. Pluggable duplication validation strategy (Ticket #4 requirement)
        strategy = settings.processing.pluggable_duplicate_detection
        
        if strategy == "filename_size":
            stmt = select(Document).where(
                Document.name == sanitized_name,
                Document.file_size == file_size,
                Document.is_active == True
            )
            duplicate = db.scalar(stmt)
            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A duplicate upload detected: '{sanitized_name}' has already been processed."
                )
                
        elif strategy == "sha256":
            file_hash = hashlib.sha256(file_content).hexdigest()
            # Perform query checking SHA-256 metadata parameter
            stmt = select(Document).where(
                Document.is_active == True
            )
            documents = db.scalars(stmt).all()
            for doc in documents:
                if doc.doc_metadata.get("checksum") == file_hash:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Duplicate content detected: An identical file has already been uploaded."
                    )

        return sanitized_name
