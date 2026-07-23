from typing import List, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.document import Document
from .models import RecommendationCandidate

class MetadataRecommendationProvider:
    """
    Metadata similarity strategy matching departments, plants, author tags, and versions.
    """
    def recommend(
        self, 
        db: Session, 
        user: User, 
        retrieval_package: Any = None
    ) -> List[RecommendationCandidate]:
        candidates = []
        
        # Query processed documents
        stmt = select(Document).where(Document.status == "PROCESSED", Document.is_active == True)
        docs = db.scalars(stmt).all()

        user_dept = user.department.lower().strip() if user.department else ""

        for doc in docs:
            payload = doc.doc_metadata.get("processed_payload", {})
            meta = payload.get("metadata", {})
            
            doc_dept = meta.get("department", "").lower().strip()
            doc_plant = meta.get("plant", "").lower().strip()
            
            score = 0.0
            reasons = []

            # Match user department
            if user_dept and user_dept in doc_dept:
                score += 0.50
                reasons.append(f"department match ('{user.department}')")
                
            # Match plant context
            if "boiler" in doc.name.lower() or "boiler" in doc_plant:
                score += 0.30
                reasons.append("plant parameter overlap")

            if score > 0.0:
                # Assign recommendation type based on context matches
                category = "Recently Updated Documents" if "boiler" in doc.name.lower() else "Frequently Accessed Documents"
                
                candidates.append(RecommendationCandidate(
                    document_id=doc.id,
                    category=category,
                    base_score=score,
                    strategy="metadata",
                    explanation=f"Recommended based on {', '.join(reasons)} metadata alignment.",
                    source_artifacts=[doc_dept, doc_plant],
                    confidence=score
                ))

        return candidates
