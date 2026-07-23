from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.models.document import Document
from app.models.access_request import AccessRequest
from app.services.policy import PolicyEngine
from .grants import AccessGrantsManager
from .history import AccessControlHistory
from .events import AccessControlEvents

class AccessApprovalsManager:
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
        # 1. Fetch document
        stmt_doc = select(Document).where(Document.id == document_id)
        document = db.scalar(stmt_doc)
        if not document or not document.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target document not found or inactive."
            )

        # 2. Query PolicyEngine clearance permissions
        # Do NOT pass database session here to keep PolicyEngine pure
        decision = PolicyEngine.evaluate_view_document(requester, document)
        if decision.allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Clearance override request rejected: You already hold sufficient security clearance."
            )

        if not decision.can_request_override:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Clearance override request rejected: Category clearance limits restrict manual overrides."
            )

        # 3. Check for existing pending requests
        stmt_pending = select(AccessRequest).where(
            AccessRequest.requester_id == requester.id,
            AccessRequest.document_id == document_id,
            AccessRequest.status == "Pending"
        )
        existing_request = db.scalar(stmt_pending)
        if existing_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A pending clearance request already exists for this resource."
            )

        # 4. Save new request
        req = AccessRequest(
            requester_id=requester.id,
            document_id=document_id,
            requested_sections=requested_sections,
            justification=justification,
            status="Pending"
        )
        db.add(req)
        db.commit()
        db.refresh(req)

        # 5. Log history and fire event hook
        AccessControlHistory.log_action(
            db=db,
            request_id=req.id,
            actor_id=requester.id,
            action="create",
            remarks="Clearance request submitted."
        )
        
        AccessControlEvents.on_request_created(req.id, requester.name, document.name)

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
        # 1. Validate reviewer permissions
        review_decision = PolicyEngine.evaluate_approve_override_action(reviewer)
        if not review_decision.allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=review_decision.reason
            )

        # 2. Fetch pending request
        stmt_req = select(AccessRequest).where(AccessRequest.id == request_id)
        req = db.scalar(stmt_req)
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Access override request not found."
            )

        if req.status != "Pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Request cannot be approved. Current state: {req.status}."
            )

        # 3. Update status
        req.status = "Approved"
        db.commit()

        # 4. Generate active temporary grant
        AccessGrantsManager.create_grant(
            db=db,
            request_id=req.id,
            user_id=req.requester_id,
            document_id=req.document_id,
            allowed_sections=req.requested_sections,
            valid_hours=valid_hours,
            granted_by=reviewer.id
        )

        # 5. Log audit history and trigger hook
        AccessControlHistory.log_action(
            db=db,
            request_id=req.id,
            actor_id=reviewer.id,
            action="approve",
            remarks=remarks
        )

        AccessControlEvents.on_request_approved(req.id, reviewer.name, valid_hours)

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
        # 1. Validate reviewer permissions
        review_decision = PolicyEngine.evaluate_approve_override_action(reviewer)
        if not review_decision.allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=review_decision.reason
            )

        # 2. Fetch pending request
        stmt_req = select(AccessRequest).where(AccessRequest.id == request_id)
        req = db.scalar(stmt_req)
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Access override request not found."
            )

        if req.status != "Pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Request cannot be rejected. Current state: {req.status}."
            )

        # 3. Update status
        req.status = "Rejected"
        db.commit()

        # 4. Log history and trigger event hook
        AccessControlHistory.log_action(
            db=db,
            request_id=req.id,
            actor_id=reviewer.id,
            action="reject",
            remarks=remarks
        )

        AccessControlEvents.on_request_rejected(req.id, reviewer.name, remarks)

        return req

    @staticmethod
    def cancel_request(db: Session, requester: User, request_id: int) -> AccessRequest:
        """
        Cancels a pending request before it gets reviewed by compliance administrators.
        """
        stmt_req = select(AccessRequest).where(AccessRequest.id == request_id)
        req = db.scalar(stmt_req)
        if not req:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Access override request not found."
            )

        # Ensure requester ownership
        if req.requester_id != requester.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied: You can only cancel override requests you submitted."
            )

        if req.status != "Pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Request cannot be cancelled. Current state: {req.status}."
            )

        # Cancel request
        req.status = "Cancelled"
        db.commit()

        # Log history
        AccessControlHistory.log_action(
            db=db,
            request_id=req.id,
            actor_id=requester.id,
            action="cancel",
            remarks="Request cancelled by requester."
        )

        return req
