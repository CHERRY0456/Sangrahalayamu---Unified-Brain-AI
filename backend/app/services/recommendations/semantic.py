import re
from typing import List, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.document import Document
from .models import RecommendationCandidate

class SemanticRecommendationProvider:
    """
    Semantic context recommendation strategy suggesting follow-up items based on active queries.
    """
    def recommend(
        self, 
        db: Session, 
        user: User, 
        current_query: str = None,
        retrieval_package: Any = None
    ) -> List[RecommendationCandidate]:
        candidates = []
        if not current_query:
            return candidates

        query_terms = set(re.findall(r"\w+", current_query.lower()))
        
        # Query processed documents
        stmt = select(Document).where(Document.status == "PROCESSED", Document.is_active == True)
        docs = db.scalars(stmt).all()

        for doc in docs:
            payload = doc.doc_metadata.get("processed_payload", {})
            chunks = payload.get("chunks", [])
            
            # Find the best keyword overlap matching terms
            max_overlap = 0
            for ch in chunks:
                chunk_terms = set(re.findall(r"\w+", ch.get("text", "").lower()))
                overlap = len(query_terms.intersection(chunk_terms))
                if overlap > max_overlap:
                    max_overlap = overlap

            if max_overlap > 0:
                jaccard_score = max_overlap / max(1, len(query_terms))
                candidates.append(RecommendationCandidate(
                    document_id=doc.id,
                    category="Compliance References",
                    base_score=jaccard_score,
                    strategy="semantic",
                    explanation=(
                        f"Recommended because '{doc.name}' contains chunks with "
                        f"{int(jaccard_score * 100)}% keyword similarity matching the current query."
                    ),
                    source_artifacts=list(query_terms),
                    confidence=jaccard_score
                ))

        return candidates
