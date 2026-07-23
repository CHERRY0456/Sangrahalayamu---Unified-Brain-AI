from datetime import datetime
from sqlalchemy.orm import Session
from app.models.document import Document

class ProcessingStatusManager:
    """
    Coordinates status state changes of the Document during processing lifecycle.
    Stores failure details inside JSON metadata fields.
    """
    @staticmethod
    def set_processing(db: Session, doc: Document) -> None:
        """
        Transitions document status to PROCESSING and increments retry counts.
        """
        doc.status = "PROCESSING"
        
        # Copy dictionary to trigger SQLAlchemy JSON change tracking
        meta = dict(doc.doc_metadata or {})
        meta["retry_count"] = meta.get("retry_count", 0) + 1
        
        # Clear past error keys
        meta.pop("error_reason", None)
        meta.pop("failure_timestamp", None)
        
        doc.doc_metadata = meta
        db.commit()

    @staticmethod
    def set_processed(db: Session, doc: Document) -> None:
        """
        Transitions document status to PROCESSED.
        """
        doc.status = "PROCESSED"
        db.commit()

    @staticmethod
    def set_failed(db: Session, doc: Document, error_reason: str) -> None:
        """
        Transitions document status to FAILED and logs error characteristics.
        """
        doc.status = "FAILED"
        
        meta = dict(doc.doc_metadata or {})
        meta["error_reason"] = error_reason
        meta["failure_timestamp"] = datetime.utcnow().isoformat()
        
        doc.doc_metadata = meta
        db.commit()
