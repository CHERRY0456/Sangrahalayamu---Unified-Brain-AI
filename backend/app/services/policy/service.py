from typing import Optional, List
from app.models.user import User
from app.models.document import Document
from app.schemas.policy import PolicyDecision

from .clearance import ClearanceEvaluator
from .permissions import PermissionEvaluator
from .section_access import SectionAccessEvaluator

class PolicyEngine:
    @staticmethod
    def evaluate_view_document(
        user: User, 
        document: Document, 
        has_active_override: bool = False
    ) -> PolicyDecision:
        """
        Evaluates if the user is authorized to view the metadata and general contents of a document.
        Takes 'has_active_override' from caller database checks to keep PolicyEngine decoupled from tables.
        """
        user_role = user.role.name
        user_permissions = user.role.permissions
        
        # 1. Check if override clearance was already resolved by the caller (AccessControlService)
        if has_active_override:
            return PolicyDecision(
                allowed=True,
                reason="Access authorized via active approved override clearance grant.",
                required_clearance=document.required_clearance,
                user_clearance=ClearanceEvaluator.get_user_clearance(user_role),
                audit_reason="OVERRIDE_GRANTED"
            )
            
        # 2. Check RBAC permissions - User must have at least one reading permission (chat, history, transparency)
        has_read_permission = any(
            perm in user_permissions for perm in ["chat", "history", "transparency", "audit"]
        )
        if not has_read_permission:
            return PolicyDecision(
                allowed=False,
                reason="Insufficient role permissions to access document resources.",
                required_permission="chat|history|transparency",
                audit_reason="RBAC_READ_FAILED"
            )
            
        # 3. Check clearance level
        user_clearance = ClearanceEvaluator.get_user_clearance(user_role)
        required_clearance = document.required_clearance
        
        if not ClearanceEvaluator.is_clearance_sufficient(user_clearance, required_clearance):
            # Users can request override for any document except LEVEL_5 (Executive secrets)
            can_request = required_clearance != "LEVEL_5"
            return PolicyDecision(
                allowed=False,
                reason="Insufficient security clearance to view this document classification tier.",
                required_clearance=required_clearance,
                user_clearance=user_clearance,
                can_request_override=can_request,
                audit_reason="CLEARANCE_INSUFFICIENT"
            )
            
        return PolicyDecision(
            allowed=True,
            reason="Clearance level and role permissions authorized.",
            required_clearance=required_clearance,
            user_clearance=user_clearance,
            audit_reason="AUTH_SUCCESS"
        )

    @staticmethod
    def evaluate_chat_with_document(
        user: User, 
        document: Document, 
        has_active_override: bool = False
    ) -> PolicyDecision:
        """
        Evaluates if the user can use the RAG model to chat/interact with the document.
        """
        user_permissions = user.role.permissions
        
        # Must have chat permission tag
        if "chat" not in user_permissions:
            return PolicyDecision(
                allowed=False,
                reason="Your role is not authorized to interact with the conversational AI search engine.",
                required_permission="chat",
                audit_reason="RBAC_CHAT_FAILED"
            )
            
        # Must pass general document view check
        return PolicyEngine.evaluate_view_document(user, document, has_active_override=has_active_override)

    @staticmethod
    def evaluate_download_document(
        user: User, 
        document: Document, 
        has_active_override: bool = False
    ) -> PolicyDecision:
        """
        Evaluates if the user can download/export the document file.
        """
        # For security, download requires transparency or upload permissions
        user_permissions = user.role.permissions
        has_dl_permission = any(perm in user_permissions for perm in ["transparency", "upload"])
        
        if not has_dl_permission:
            return PolicyDecision(
                allowed=False,
                reason="Insufficient role permission to download raw assets.",
                required_permission="transparency|upload",
                audit_reason="RBAC_DOWNLOAD_FAILED"
            )
            
        return PolicyEngine.evaluate_view_document(user, document, has_active_override=has_active_override)

    @staticmethod
    def evaluate_view_section(
        user: User, 
        document: Document, 
        section_name: str,
        has_active_override: bool = False,
        allowed_sections: Optional[List[str]] = None
    ) -> PolicyDecision:
        """
        Evaluates section, paragraph, or chunk access levels.
        Takes 'allowed_sections' array resolved by caller database lookup context.
        """
        user_role = user.role.name
        user_clearance = ClearanceEvaluator.get_user_clearance(user_role)
        
        # 1. Check if active override explicitly covers this section name
        if has_active_override and allowed_sections:
            is_allowed_sec = any(
                sec.lower().strip() in ["entire document", section_name.lower().strip()]
                for sec in allowed_sections
            )
            if is_allowed_sec:
                return PolicyDecision(
                    allowed=True,
                    reason=f"Access to {section_name} authorized via active approved override grant.",
                    required_clearance=document.required_clearance,
                    user_clearance=user_clearance,
                    audit_reason="SECTION_OVERRIDE_GRANTED"
                )
        
        # 2. Evaluate general view permissions (without assuming override for non-matching sections)
        has_base_clearance = ClearanceEvaluator.is_clearance_sufficient(
            user_clearance, document.required_clearance
        )
        
        # If they rely on override but this section is not allowed, evaluate as if no override is present
        effective_override = has_active_override
        if not has_base_clearance and has_active_override:
            is_allowed_sec = False
            if allowed_sections:
                is_allowed_sec = any(
                    sec.lower().strip() in ["entire document", section_name.lower().strip()]
                    for sec in allowed_sections
                )
            if not is_allowed_sec:
                effective_override = False

        view_decision = PolicyEngine.evaluate_view_document(
            user, document, has_active_override=effective_override
        )
        if not view_decision.allowed:
            return view_decision
            
        # 3. Check granular section exclusions (exclusions do not apply if overridden via grants)
        if not has_active_override:
            if not SectionAccessEvaluator.is_section_accessible(user_role, document.doc_metadata, section_name):
                return PolicyDecision(
                    allowed=False,
                    reason=f"Access to {section_name} is excluded for your role designation.",
                    required_clearance=document.required_clearance,
                    user_clearance=user_clearance,
                    can_request_override=True,  # Users can request section override
                    audit_reason="SECTION_EXCLUDED"
                )
            
        return PolicyDecision(
            allowed=True,
            reason=f"Access to {section_name} authorized.",
            required_clearance=document.required_clearance,
            user_clearance=user_clearance,
            audit_reason="SECTION_AUTH_SUCCESS"
        )

    @staticmethod
    def evaluate_upload_action(user: User) -> PolicyDecision:
        """
        Evaluates if the user is authorized to upload new files.
        """
        user_role = user.role.name
        user_permissions = user.role.permissions
        user_clearance = ClearanceEvaluator.get_user_clearance(user_role)
        
        if "upload" not in user_permissions:
            return PolicyDecision(
                allowed=False,
                reason="Your role is not authorized to ingest new documentation assets.",
                required_permission="upload",
                user_clearance=user_clearance,
                audit_reason="UPLOAD_DENIED"
            )
            
        return PolicyDecision(
            allowed=True,
            reason="Upload action authorized.",
            required_permission="upload",
            user_clearance=user_clearance,
            audit_reason="UPLOAD_AUTHORIZED"
        )

    @staticmethod
    def evaluate_audit_view_action(user: User) -> PolicyDecision:
        """
        Evaluates if the user is authorized to view audit logs or compliance trackers.
        """
        user_role = user.role.name
        user_permissions = user.role.permissions
        user_clearance = ClearanceEvaluator.get_user_clearance(user_role)
        
        if "audit" not in user_permissions:
            return PolicyDecision(
                allowed=False,
                reason="Access Denied: Compliance audits require specific administrative clearances.",
                required_permission="audit",
                user_clearance=user_clearance,
                audit_reason="AUDIT_VIEW_DENIED"
            )
            
        return PolicyDecision(
            allowed=True,
            reason="Audit viewing authorized.",
            required_permission="audit",
            user_clearance=user_clearance,
            audit_reason="AUDIT_VIEW_AUTHORIZED"
        )

    @staticmethod
    def evaluate_approve_override_action(user: User) -> PolicyDecision:
        """
        Evaluates if the user is authorized to approve or reject clearance requests.
        Only LEVEL_4 and LEVEL_5 roles with audit permissions are eligible.
        """
        user_role = user.role.name
        user_permissions = user.role.permissions
        user_clearance = ClearanceEvaluator.get_user_clearance(user_role)
        
        # Requires audit permission and at least LEVEL_4 clearance
        has_audit = "audit" in user_permissions
        has_level = ClearanceEvaluator.is_clearance_sufficient(user_clearance, "LEVEL_4")
        
        if not (has_audit and has_level):
            return PolicyDecision(
                allowed=False,
                reason="Only compliance officers or board executives are authorized to approve clearance overrides.",
                required_permission="audit",
                required_clearance="LEVEL_4",
                user_clearance=user_clearance,
                audit_reason="APPROVE_ACTION_DENIED"
            )
            
        return PolicyDecision(
            allowed=True,
            reason="Clearance approval authorization granted.",
            required_permission="audit",
            required_clearance="LEVEL_4",
            user_clearance=user_clearance,
            audit_reason="APPROVE_ACTION_AUTHORIZED"
        )
