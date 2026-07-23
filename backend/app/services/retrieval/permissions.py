from typing import List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.document import Document
from app.services.policy import PolicyEngine
from app.services.access_control import AccessControlService
from .models import RetrievalMatch

class RetrievalPermissionFilter:
    """
    Enforces security clearances and active temporary overrides on retrieved candidates.
    Filters out chunks or sections user is not authorized to view.
    """
    @staticmethod
    def filter_authorized_chunks(
        db: Session, 
        user: User, 
        matches: List[RetrievalMatch]
    ) -> List[RetrievalMatch]:
        """
        Runs PolicyEngine checks for document and section permissions, resolving active grants.
        """
        # Cache evaluation parameters per document ID to prevent duplicate DB pings
        doc_eval_cache: Dict[int, Tuple[bool, Any, bool, List[str]]] = {}
        
        authorized_matches: List[RetrievalMatch] = []
        
        for m in matches:
            doc_id = m.metadata.get("document_id")
            if not doc_id:
                continue
                
            section = m.metadata.get("section", "Introduction")
            
            if doc_id not in doc_eval_cache:
                stmt = select(Document).where(Document.id == doc_id)
                doc = db.scalar(stmt)
                if not doc:
                    doc_eval_cache[doc_id] = (False, None, False, [])
                    continue

                # Query database Access Control overrides context (Ticket #3 models check)
                has_override = AccessControlService.has_active_override(db, user.id, doc_id)
                allowed_sections = AccessControlService.get_active_grant_sections(db, user.id, doc_id)

                # Query decoupled PolicyEngine view permissions
                view_decision = PolicyEngine.evaluate_view_document(
                    user=user,
                    document=doc,
                    has_active_override=has_override
                )
                
                # Emit authorization event (Ticket #11 constraint)
                try:
                    from app.services.audit import audit_service, AuditEvent, EVENT_TYPE_AUTHORIZATION
                    audit_service.record_event(db, AuditEvent(
                        event_type=EVENT_TYPE_AUTHORIZATION,
                        actor_id=user.id,
                        actor_role=user.role.name if user.role else "User",
                        resource_type="document",
                        resource_id=str(doc.id),
                        action="evaluate_view_document",
                        status="SUCCESS" if view_decision.allowed else "DENIED",
                        source_service="policy_engine",
                        metadata={"reason": view_decision.reason, "audit_reason": view_decision.audit_reason}
                    ))
                except Exception:
                    pass
                
                doc_eval_cache[doc_id] = (view_decision.allowed, doc, has_override, allowed_sections)

            # Retrieve cached attributes
            allowed, doc, has_override, allowed_sections = doc_eval_cache[doc_id]
            if not allowed:
                continue  # Exclude chunk: User lacks clearance
                
            # Perform section-level exclusions and override checks
            sec_decision = PolicyEngine.evaluate_view_section(
                user=user,
                document=doc,
                section_name=section,
                has_active_override=has_override,
                allowed_sections=allowed_sections
            )
            
            if sec_decision.allowed:
                authorized_matches.append(m)

        return authorized_matches
