import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.services.retrieval.models import HybridRetrievalPackage
from .models import RecommendationPackage, RecommendationCandidate, Recommendation
from .provider_factory import RecommendationProviderFactory
from .permissions import RecommendationPermissionFilter
from .ranking import RecommendationRanker

logger = logging.getLogger("sangrahalayamu.recommendations.orchestrator")

class RecommendationService:
    """
    Central Recommendation orchestrator generating permission-aware recommendations (Ticket #10 constraint).
    """
    def generate_recommendations(
        self,
        db: Session,
        user: User,
        current_query: Optional[str] = None,
        ai_response: Optional[Any] = None,
        retrieval_package: Optional[HybridRetrievalPackage] = None
    ) -> RecommendationPackage:
        if not settings.flags.enable_recommendations:
            return RecommendationPackage(warnings=["RECOMMENDATIONS_DISABLED"])

        # 1. Gather candidates from active strategies
        providers = RecommendationProviderFactory.get_providers()
        all_candidates: List[RecommendationCandidate] = []

        for prov in providers:
            try:
                # Handle dynamic signatures matching strategy requirements
                if hasattr(prov, "recommend"):
                    if prov.__class__.__name__ == "SemanticRecommendationProvider":
                        cands = prov.recommend(
                            db=db,
                            user=user,
                            current_query=current_query,
                            retrieval_package=retrieval_package
                        )
                    else:
                        cands = prov.recommend(
                            db=db,
                            user=user,
                            retrieval_package=retrieval_package
                        )
                    all_candidates.extend(cands)
            except Exception as e:
                logger.error(f"Strategy provider '{prov.__class__.__name__}' execution failed: {str(e)}")

        # 2. Filter candidates by Policy clearance
        filtered_candidates = RecommendationPermissionFilter.filter_candidates(
            db=db,
            user=user,
            candidates=all_candidates
        )

        warnings_list = []
        is_cold_start = (current_query is None and retrieval_package is None)
        if is_cold_start:
            warnings_list.append("COLD_START_ACTIVATED")

        # 3. Cold-Start handling: if no interaction/overlap candidates found
        if not filtered_candidates:
            if "COLD_START_ACTIVATED" not in warnings_list:
                warnings_list.append("COLD_START_ACTIVATED")
            logger.info("Cold-start triggered. Suggesting fallback recommendations based on user department.")
            
            # Suggest general department documentation candidates
            from app.models.document import Document
            from sqlalchemy import select
            doc_stmt = select(Document).where(Document.status == "PROCESSED", Document.is_active == True)
            docs = db.scalars(doc_stmt).all()
            
            for doc in docs:
                payload = doc.doc_metadata.get("processed_payload", {})
                dept = payload.get("metadata", {}).get("department", "").lower()
                user_dept = user.department.lower() if user.department else ""
                
                if user_dept and user_dept in dept:
                    filtered_candidates.append(RecommendationCandidate(
                        document_id=doc.id,
                        category="Frequently Accessed Documents",
                        base_score=0.50,
                        strategy="cold_start",
                        explanation=f"Suggested department documentation for {user.department}.",
                        source_artifacts=[user.department],
                        confidence=0.50
                    ))

            # Apply clearance guards to fallback candidates as well
            filtered_candidates = RecommendationPermissionFilter.filter_candidates(
                db=db,
                user=user,
                candidates=filtered_candidates
            )

        # 4. Strategy-Agnostic Ranking
        ranked_recs = RecommendationRanker.rank_candidates(
            db=db,
            candidates=filtered_candidates,
            max_recommendations=5
        )

        # Compile summaries and category counts
        cat_summary = {}
        sources_list = []
        for rec in ranked_recs:
            cat_summary[rec.category] = cat_summary.get(rec.category, 0) + 1
            sources_list.extend(rec.source_documents)

        ranking_weights = {
            "graph_relevance": 0.35,
            "metadata_similarity": 0.30,
            "semantic_similarity": 0.15,
            "usage_frequency": 0.20
        }

        package = RecommendationPackage(
            recommendations=ranked_recs,
            category_summary=cat_summary,
            ranking_details={"weights_applied": ranking_weights, "total_candidates_evaluated": len(all_candidates)},
            sources=list(set(sources_list)),
            warnings=warnings_list
        )

        # Emit recommendation audit event (Ticket #11 constraint)
        try:
            from app.services.audit import audit_service, AuditEvent, EVENT_TYPE_RECOMMENDATION
            audit_service.record_event(db, AuditEvent(
                event_type=EVENT_TYPE_RECOMMENDATION,
                actor_id=user.id,
                actor_role=user.role.name if user.role else "User",
                action="generate_recommendations",
                status="SUCCESS",
                source_service="recommendation_engine",
                metadata={"recommendations_returned": len(ranked_recs), "warnings": warnings_list}
            ))
        except Exception:
            pass

        return package

# Global singleton instance for endpoint imports
recommendation_service = RecommendationService()
