import uuid
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.document import Document
from app.core.config import settings
from app.core.constants import ROLE_CLEARANCE_MAP, CLEARANCE_LEVELS, CLASSIFICATION_CLEARANCE_MAP

class UploadMetadataRegistry:
    @staticmethod
    def register_metadata(
        db: Session, 
        user: User, 
        original_name: str, 
        stored_name: str, 
        mime_type: str, 
        file_size: int,
        checksum: str,
        doc_uuid: str
    ) -> Document:
        """
        Builds and saves the extended Document model record in the database.
        """
        # Resolve classification and clearance configs
        classification = settings.processing.default_doc_classification
        required_clearance = CLASSIFICATION_CLEARANCE_MAP.get(classification, "LEVEL_1")
        
        # Store checksum and properties in doc_metadata JSON
        doc_metadata = {
            "checksum": checksum,
            "original_filename": original_name,
            "section_exclusions": {}
        }
        
        document = Document(
            uuid=doc_uuid,
            name=original_name,
            stored_name=stored_name,
            mime_type=mime_type,
            file_size=file_size,
            classification=classification,
            required_clearance=required_clearance,
            department=user.department,
            status="UPLOADED",
            doc_metadata=doc_metadata,
            uploaded_by_id=user.id,
            is_active=True
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
