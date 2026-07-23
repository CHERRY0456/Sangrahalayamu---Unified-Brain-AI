from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.access_request import AccessRequest
from app.models.user import User

from .approvals import AccessApprovalsManager
from .grants import AccessGrantsManager

class AccessControlService:
    @staticmethod
    def create_request(
        db: Session, 
        requester: User, 
        document_id: int, 
        requested_sections: List[str], 
        justification: str
    ) -> AccessRequest:
        """
        Creates a new override request after checking PolicyEngine permissions.
        """
        req = AccessApprovalsManager.create_request(
            db, requester, document_id, requested_sections, justification
        )
        try:
            from app.services.audit import audit_service, AuditEvent, EVENT_TYPE_ACCESS_OVERRIDE
            audit_service.record_event(db, AuditEvent(
                event_type=EVENT_TYPE_ACCESS_OVERRIDE,
                actor_id=requester.id,
                actor_role=requester.role.name if requester.role else "User",
                resource_type="document",
                resource_id=str(document_id),
                action="request_access",
                status="SUCCESS",
                source_service="access_control",
                metadata={"request_id": req.id, "sections": requested_sections}
            ))
        except Exception:
            pass
        # Notify requester — access request submitted
        try:
            from app.services.notifications.service import notification_service
            from app.services.notifications.models import NotificationRequest
            notification_service.send_notification(db, NotificationRequest(
                event_type="ACCESS_REQUEST_SUBMITTED",
                recipient_id=requester.id,
                priority="INFO",
                title="Access Override Request Submitted",
                message=f"Your access request for document #{document_id} (sections: {', '.join(requested_sections)}) has been submitted and is pending review.",
                metadata={"document_id": document_id, "sections": requested_sections},
            ))
        except Exception:
            pass
        return req

    @staticmethod
    def approve_request(
        db: Session, 
        reviewer: User, 
        request_id: int, 
        remarks: str,
        valid_hours: int = 24
    ) -> AccessRequest:
        """
        Approves a pending override request, creating an active AccessGrant.
        """
        req = AccessApprovalsManager.approve_request(
            db, reviewer, request_id, remarks, valid_hours
        )
        try:
            from app.services.audit import audit_service, AuditEvent, EVENT_TYPE_ACCESS_OVERRIDE
            audit_service.record_event(db, AuditEvent(
                event_type=EVENT_TYPE_ACCESS_OVERRIDE,
                actor_id=reviewer.id,
                actor_role=reviewer.role.name if reviewer.role else "User",
                resource_type="access_request",
                resource_id=str(request_id),
                action="approve_access",
                status="SUCCESS",
                source_service="access_control",
                metadata={"remarks": remarks, "valid_hours": valid_hours}
            ))
        except Exception:
            pass
        # Notify requester — access approved
        try:
            from app.services.notifications.service import notification_service
            from app.services.notifications.models import NotificationRequest
            notification_service.send_notification(db, NotificationRequest(
                event_type="ACCESS_APPROVED",
                recipient_id=req.requester_id,
                priority="INFO",
                title="Access Override Request Approved",
                message=f"Your access request #{request_id} has been approved. Remarks: {remarks}.",
                metadata={"request_id": request_id, "remarks": remarks, "valid_hours": valid_hours},
            ))
        except Exception:
            pass
        return req

    @staticmethod
    def reject_request(
        db: Session, 
        reviewer: User, 
        request_id: int, 
        remarks: str
    ) -> AccessRequest:
        """
        Rejects a pending override request.
        """
        req = AccessApprovalsManager.reject_request(
            db, reviewer, request_id, remarks
        )
        try:
            from app.services.audit import audit_service, AuditEvent, EVENT_TYPE_ACCESS_OVERRIDE
            audit_service.record_event(db, AuditEvent(
                event_type=EVENT_TYPE_ACCESS_OVERRIDE,
                actor_id=reviewer.id,
                actor_role=reviewer.role.name if reviewer.role else "User",
                resource_type="access_request",
                resource_id=str(request_id),
                action="reject_access",
                status="SUCCESS",
                source_service="access_control",
                metadata={"remarks": remarks}
            ))
        except Exception:
            pass
        # Notify requester — access rejected
        try:
            from app.services.notifications.service import notification_service
            from app.services.notifications.models import NotificationRequest
            notification_service.send_notification(db, NotificationRequest(
                event_type="ACCESS_REJECTED",
                recipient_id=req.requester_id,
                priority="WARNING",
                title="Access Override Request Rejected",
                message=f"Your access request #{request_id} was rejected. Remarks: {remarks}.",
                metadata={"request_id": request_id, "remarks": remarks},
            ))
        except Exception:
            pass
        return req

    @staticmethod
    def cancel_request(db: Session, requester: User, request_id: int) -> AccessRequest:
        """
        Cancels a pending request before review.
        """
        return AccessApprovalsManager.cancel_request(db, requester, request_id)

    @staticmethod
    def get_request(db: Session, request_id: int) -> Optional[AccessRequest]:
        """
        Fetches an override request by ID.
        """
        stmt = select(AccessRequest).where(AccessRequest.id == request_id)
        return db.scalar(stmt)

    @staticmethod
    def list_pending_requests(db: Session) -> List[AccessRequest]:
        """
        Lists all override requests awaiting administrator review.
        """
        stmt = select(AccessRequest).where(AccessRequest.status == "Pending").order_by(
            AccessRequest.created_at.desc()
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def list_all_requests(db: Session) -> List[AccessRequest]:
        """
        Lists all requests.
        """
        stmt = select(AccessRequest).order_by(AccessRequest.created_at.desc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def has_active_override(db: Session, user_id: int, document_id: int, section_name: str = None) -> bool:
        """
        Queries if there is an active temporary override for this user and document.
        """
        return AccessGrantsManager.has_active_override(db, user_id, document_id, section_name)

    @staticmethod
    def get_active_grant_sections(db: Session, user_id: int, document_id: int) -> List[str]:
        """
        Retrieves sections currently unlocked by active approved overrides.
        """
        return AccessGrantsManager.get_active_grant_sections(db, user_id, document_id)

    @staticmethod
    def expire_overrides(db: Session) -> int:
        """
        Sweeps the grants database to auto-expire temporary permissions.
        """
        return AccessGrantsManager.expire_overrides(db)
