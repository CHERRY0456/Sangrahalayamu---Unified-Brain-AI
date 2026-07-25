import logging
import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.document import Document
from app.services.policy import PolicyEngine
from app.services.storage import storage_service
from .validator import UploadValidator
from .metadata import UploadMetadataRegistry

# Setup logger for basic audit capture
logger = logging.getLogger("sangrahalayamu.upload")

class UploadService:
    @staticmethod
    def upload_file(
        db: Session, 
        user: User, 
        file_content: bytes, 
        filename: str, 
        content_type: str
    ) -> Document:
        """
        Validates the upload, stores file binary, saves database metadata and audits.
        """
        # 1. Enforce upload permissions via centralized PolicyEngine
        decision = PolicyEngine.evaluate_upload_action(user)
        if not decision.allowed:
            # Audit log failure
            logger.warning(
                f"Audit Log [Upload Failure]: User '{user.email}' attempted to upload '{filename}' "
                f"but was blocked. Reason: '{decision.reason}'"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=decision.reason
            )

        # 2. File and pluggable duplicate validation
        sanitized_name = UploadValidator.validate_file(db, filename, content_type, file_content)

        # 3. Generate unique document UUID first (to form version-ready storage keys)
        doc_uuid = str(uuid.uuid4())

        # 4. Store via global StorageService singleton (returns structured StorageResult)
        result = storage_service.store_document(
            file_content=file_content,
            filename=sanitized_name,
            doc_uuid=doc_uuid
        )
        if not result.success:
            logger.error(
                f"Audit Log [Upload Failure]: Storage provider failure writing '{sanitized_name}' "
                f"for user '{user.email}'. Reason: {result.error_message}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Storage failure: Could not persist uploaded document."
            )

        # 5. Save metadata record (stored_name holds the database storage key)
        doc = UploadMetadataRegistry.register_metadata(
            db=db,
            user=user,
            original_name=sanitized_name,
            stored_name=result.storage_key,  # Store only virtual storage_key in Document.stored_name
            mime_type=content_type,
            file_size=result.size,
            checksum=result.checksum,
            doc_uuid=doc_uuid
        )

        # Emit upload audit event (Ticket #11 constraint)
        try:
            from app.services.audit import audit_service, AuditEvent, EVENT_TYPE_UPLOAD
            audit_service.record_event(db, AuditEvent(
                event_type=EVENT_TYPE_UPLOAD,
                actor_id=user.id,
                actor_role=user.role.name if user.role else "User",
                resource_type="document",
                resource_id=str(doc.id),
                action="upload_file",
                status="SUCCESS",
                source_service="upload_service",
                metadata={"filename": sanitized_name, "size": result.size}
            ))
        except Exception:
            pass

        # Notify uploader — upload success (Ticket #12)
        try:
            from app.services.notifications.service import notification_service
            from app.services.notifications.models import NotificationRequest
            notification_service.send_notification(db, NotificationRequest(
                event_type="UPLOAD_SUCCESS",
                recipient_id=user.id,
                priority="INFO",
                title="Document Uploaded Successfully",
                message=f"File '{sanitized_name}' ({result.size} bytes) was uploaded successfully.",
                metadata={"filename": sanitized_name, "size": result.size, "document_id": doc.id},
            ))
        except Exception:
            pass

        # 6. Log success audit event
        logger.info(
            f"Audit Log [Upload Success]: User '{user.email}' successfully uploaded document "
            f"ID '{doc.id}' (UUID: {doc.uuid}, Key: '{result.storage_key}', Size: {result.size} bytes)."
        )

        # 7. Asynchronously trigger document processing pipeline in a background thread
        # Immediately returns HTTP 201 (< 50ms) to prevent client-side HTTP timeouts!
        def _async_process_document(doc_id: int):
            from app.database.session import SessionLocal
            from app.services.processing.pipeline import DocumentProcessingPipeline
            bg_db = SessionLocal()
            try:
                logger.info(f"[UploadService] Background processing worker started for doc_id={doc_id}.")
                DocumentProcessingPipeline.process_document(bg_db, doc_id)
                logger.info(f"[UploadService|SUCCESS] Background processing worker completed for doc_id={doc_id}.")
            except Exception as proc_err:
                logger.error(f"[UploadService|ERROR] Background pipeline processing failed for doc_id={doc_id}: {proc_err}")
            finally:
                bg_db.close()

        import threading
        threading.Thread(target=_async_process_document, args=(doc.id,), daemon=True).start()

        return doc

    @staticmethod
    def delete_file(db: Session, user: User, document_id: int) -> None:
        """
        Deletes metadata record and delegates file removal to storage adapter.
        """
        stmt = select(Document).where(Document.id == document_id, Document.is_active == True)
        doc = db.scalar(stmt)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found."
            )

        # Ownership or compliance admin permission checks
        is_owner = doc.uploaded_by_id == user.id
        is_approver = "audit" in user.role.permissions
        if not (is_owner or is_approver):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied: You do not have permissions to delete this document."
            )

        # Call storage deletion procedure using persistent storage_key
        storage_service.delete_document(doc.stored_name)

        # Soft-delete metadata record in db
        doc.is_active = False
        db.commit()

        # Emit delete audit event (Ticket #11 constraint)
        try:
            from app.services.audit import audit_service, AuditEvent, EVENT_TYPE_UPLOAD
            audit_service.record_event(db, AuditEvent(
                event_type=EVENT_TYPE_UPLOAD,
                actor_id=user.id,
                actor_role=user.role.name if user.role else "User",
                resource_type="document",
                resource_id=str(document_id),
                action="delete_file",
                status="SUCCESS",
                source_service="upload_service",
                metadata={"filename": doc.name}
            ))
        except Exception:
            pass

        logger.info(
            f"Audit Log [Delete Success]: User '{user.email}' deleted document ID '{document_id}' "
            f"(File: '{doc.name}')."
        )

    @staticmethod
    def get_file_metadata(db: Session, user: User, document_id: int) -> Document:
        """
        Fetches document metadata details. Enforces PolicyEngine view permissions.
        """
        stmt = select(Document).where(Document.id == document_id, Document.is_active == True)
        doc = db.scalar(stmt)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found."
            )

        # Verify reading clearance via PolicyEngine
        decision = PolicyEngine.evaluate_view_document(user, doc)
        if not decision.allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=decision.reason
            )

        # Emit download/view audit event (Ticket #11 constraint)
        try:
            from app.services.audit import audit_service, AuditEvent, EVENT_TYPE_DOWNLOAD
            audit_service.record_event(db, AuditEvent(
                event_type=EVENT_TYPE_DOWNLOAD,
                actor_id=user.id,
                actor_role=user.role.name if user.role else "User",
                resource_type="document",
                resource_id=str(document_id),
                action="view_document",
                status="SUCCESS",
                source_service="upload_service",
                metadata={"filename": doc.name}
            ))
        except Exception:
            pass

        return doc

    @staticmethod
    def list_user_uploads(db: Session, user: User) -> List[Document]:
        """
        Queries all active documents uploaded by the authenticated user.
        """
        stmt = select(Document).where(
            Document.uploaded_by_id == user.id,
            Document.is_active == True
        ).order_by(Document.created_at.desc())
        return list(db.scalars(stmt).all())
