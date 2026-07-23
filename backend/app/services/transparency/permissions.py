from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.retrieval.models import HybridRetrievalPackage
from app.services.policy.clearance import ClearanceEvaluator
from app.services.access_control.grants import AccessGrantsManager
from .models import PermissionSummary

class PermissionComplianceEngine:
    @staticmethod
    def generate(
        db: Session, 
        user: User, 
        retrieval_package: HybridRetrievalPackage
    ) -> PermissionSummary:
        clearance_level = ClearanceEvaluator.get_user_clearance(user.role.name)
        
        # Check active temporary overrides in database
        from datetime import datetime
        from app.models.access_grant import AccessGrant
        grants_stmt = select(AccessGrant).where(
            AccessGrant.user_id == user.id,
            AccessGrant.expires_at > datetime.utcnow()
        )
        active_overrides = db.scalars(grants_stmt).all()
        has_override = len(active_overrides) > 0

        diagnostics = retrieval_package.diagnostics or {}
        filtered_count = diagnostics.get("matches_filtered_by_permissions", 0)

        excluded_docs = []
        excluded_secs = []
        
        if filtered_count > 0:
            excluded_docs.append("Restricted Manuals")
            excluded_secs.append("Unauthorized Sections")
            reason = (
                f"PolicyEngine restricted access to {filtered_count} candidate chunks due to "
                f"insufficient role clearance level ({clearance_level}) or unapproved section scopes."
            )
        else:
            reason = (
                f"User authorized under clearance level {clearance_level}."
            )
            if has_override:
                reason += " Active temporary override grant was applied during retrieval evaluation."

        return PermissionSummary(
            user_role=user.role.name,
            clearance_level=str(clearance_level),
            temporary_override_status=has_override,
            sections_excluded=excluded_secs,
            documents_excluded=excluded_docs,
            reason=reason,
            provenance="policy_engine"
        )
