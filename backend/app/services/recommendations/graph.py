import json
from typing import List, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.document import Document
from .models import RecommendationCandidate

class GraphRecommendationProvider:
    """
    Graph-based recommendation strategy traversing document entities and relationships.
    """
    def recommend(
        self, 
        db: Session, 
        user: User, 
        retrieval_package: Any = None
    ) -> List[RecommendationCandidate]:
        candidates = []
        
        # Extract target equipment codes from active retrieval chunks
        target_equipment = set()
        if retrieval_package and retrieval_package.chunks:
            for ch in retrieval_package.chunks:
                # Find equipment in chunks text
                import re
                codes = re.findall(r"(?:BLR|VLV|EQ)-\d+", ch.text.upper())
                target_equipment.update(codes)

        # Query all processed documents
        stmt = select(Document).where(Document.status == "PROCESSED", Document.is_active == True)
        docs = db.scalars(stmt).all()

        for doc in docs:
            payload = doc.doc_metadata.get("processed_payload", {})
            relationships = payload.get("relationships", [])
            
            for rel in relationships:
                source = rel.get("source", "").upper()
                target = rel.get("target", "").upper()
                
                # Check if this document has relationships connected to our active equipment list
                has_connection = source in target_equipment or target in target_equipment
                if has_connection:
                    # Recommend as connected SOP
                    candidates.append(RecommendationCandidate(
                        document_id=doc.id,
                        category="Related SOPs",
                        base_score=0.90,
                        strategy="graph",
                        explanation=(
                            f"Recommended because '{doc.name}' contains graph relationships "
                            f"connected to active equipment tags: {list(target_equipment)}."
                        ),
                        source_artifacts=[source, target],
                        confidence=0.85
                    ))
                    break # Recommend once per document
                    
        return candidates
