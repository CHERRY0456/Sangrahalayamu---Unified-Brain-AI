import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.document import Document
from app.services.policy import PolicyEngine
from app.services.access_control import AccessControlService
from .models import RecommendationCandidate

logger = logging.getLogger("sangrahalayamu.recommendations.permissions")

class RecommendationPermissionFilter:
    @staticmethod
    def filter_candidates(
        db: Session, 
        user: User, 
        candidates: list[RecommendationCandidate]
    ) -> list[RecommendationCandidate]:
        """
        Screens candidates, removing recommendations for documents that fail Policy Engine clearances.
        """
        allowed_candidates = []
        
        # Load doc objects cache to avoid duplicate DB queries inside loops
        doc_ids = {c.document_id for c in candidates}
        if not doc_ids:
            return allowed_candidates
            
        stmt = select(Document).where(Document.id.in_(doc_ids), Document.is_active == True)
        docs = db.scalars(stmt).all()
        doc_cache = {d.id: d for d in docs}

        for cand in candidates:
            doc = doc_cache.get(cand.document_id)
            if not doc:
                continue
                
            # Perform policy engine check matching retrieval pipeline
            has_override = AccessControlService.has_active_override(db, user.id, doc.id)
            decision = PolicyEngine.evaluate_view_document(user, doc, has_override)
            if decision.allowed:
                allowed_candidates.append(cand)
            else:
                logger.info(
                    f"Recommendation candidate document ID {cand.document_id} ('{doc.name}') "
                    f"blocked by PolicyEngine clearances for user '{user.email}'."
                )
                
        return allowed_candidates
