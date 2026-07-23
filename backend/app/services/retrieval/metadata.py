from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.document import Document
from .models import RetrievalFilters

class MetadataFilter:
    """
    Handles candidate pre-filtering on the database, parsing JSON doc_metadata properties.
    """
    @staticmethod
    def filter_candidates(db: Session, filters: Optional[RetrievalFilters]) -> List[int]:
        """
        Queries active documents, verifies metadata conditions, and returns candidate ID lists.
        """
        stmt = select(Document).where(Document.is_active == True)
        documents = db.scalars(stmt).all()
        
        if not filters:
            return [doc.id for doc in documents]

        candidate_ids = []
        for doc in documents:
            # 1. Column filters
            if filters.department and doc.department.lower() != filters.department.lower():
                continue
            if filters.classification and doc.classification.lower() != filters.classification.lower():
                continue

            # 2. JSON payload metadata filters (Ticket #5 processed payload structure)
            payload = doc.doc_metadata.get("processed_payload", {})
            payload_meta = payload.get("metadata", {})

            if filters.doc_type:
                payload_type = payload.get("doc_type", "")
                if filters.doc_type.lower() not in payload_type.lower():
                    continue
            if filters.plant:
                doc_plant = str(payload_meta.get("plant", "")).strip().lower()
                if doc_plant != str(filters.plant).strip().lower():
                    continue
            if filters.author:
                doc_author = str(payload_meta.get("author", "")).strip().lower()
                if filters.author.lower() not in doc_author:
                    continue
            if filters.version:
                doc_version = str(payload_meta.get("version", "")).strip()
                if doc_version != str(filters.version).strip():
                    continue
            if filters.equipment:
                doc_eqs = [eq.strip().lower() for eq in payload_meta.get("equipment", [])]
                # Match if at least one filter equipment code is mapped inside document
                matches_eq = any(eq.strip().lower() in doc_eqs for eq in filters.equipment)
                if not matches_eq:
                    continue

            candidate_ids.append(doc.id)

        return candidate_ids
