from typing import List, Dict, Any
from app.core.config import settings
from app.models.document import Document
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import RecommendationCandidate, Recommendation

class RecommendationRanker:
    @staticmethod
    def rank_candidates(
        db: Session,
        candidates: List[RecommendationCandidate],
        max_recommendations: int = 5
    ) -> List[Recommendation]:
        """
        Normalizes and fuses candidate scores using strategy weight coefficients (Ticket #10 constraint).
        """
        if not candidates:
            return []

        # Load weights from config
        weights = {
            "graph": 0.35,
            "metadata": 0.30,
            "semantic": 0.15,
            "usage": 0.20
        }

        # Map to query document names
        doc_ids = {c.document_id for c in candidates}
        stmt = select(Document).where(Document.id.in_(doc_ids))
        docs = db.scalars(stmt).all()
        doc_names = {d.id: d.name for d in docs}

        # Group and accumulate scores by document ID
        fused_scores: Dict[int, float] = {}
        grouped_candidates: Dict[int, List[RecommendationCandidate]] = {}

        for cand in candidates:
            doc_id = cand.document_id
            strategy = cand.strategy.lower()
            weight = weights.get(strategy, 0.10)
            
            weighted_score = cand.base_score * weight
            
            fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + weighted_score
            grouped_candidates.setdefault(doc_id, []).append(cand)

        # Sort document IDs by score desc
        sorted_docs = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)

        ranked_recommendations = []
        seen_names = set()
        for doc_id, score in sorted_docs:
            if len(ranked_recommendations) >= max_recommendations:
                break
                
            cands = grouped_candidates[doc_id]
            doc_name = doc_names.get(doc_id, f"Document ID {doc_id}")
            
            # Prevent recommending duplicate document names
            if doc_name in seen_names:
                continue
            seen_names.add(doc_name)
            
            # Select the primary category and explanation from the highest-scoring candidate
            best_cand = max(cands, key=lambda c: c.base_score)
            
            # Compile unique sources
            sources = set()
            for c in cands:
                sources.update(c.source_artifacts)

            # Limit confidence to 1.0 maximum
            confidence = min(1.0, score)

            # Map strategy to standard machine-readable reason code
            reason_map = {
                "graph": "GRAPH_RELATION",
                "metadata": "METADATA_MATCH",
                "semantic": "SEMANTIC_SIMILARITY",
                "usage": "USAGE_PATTERN",
                "cold_start": "COLD_START"
            }
            reason_code = reason_map.get(best_cand.strategy.lower(), "METADATA_MATCH")

            ranked_recommendations.append(Recommendation(
                title=f"Review manual: {doc_name}",
                category=best_cand.category,
                confidence=round(confidence, 2),
                explanation=best_cand.explanation,
                recommendation_reason_code=reason_code,
                source_documents=[doc_name]
            ))

        return ranked_recommendations
