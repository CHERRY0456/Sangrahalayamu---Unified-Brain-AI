from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.session import get_db
from app.models.user import User
from app.models.access_request import AccessRequest
from app.api.deps import get_current_user
from app.schemas.access import (
    AccessRequestCreate, 
    AccessRequestReview, 
    AccessRequestResponse, 
    AccessRequestListResponse
)
from app.services.access_control import AccessControlService

router = APIRouter(prefix="/access", tags=["access"])

def map_request_to_response(req: AccessRequest) -> AccessRequestResponse:
    """
    Utility mapper turning SQLAlchemy AccessRequest database model into serializable Pydantic model.
    """
    return AccessRequestResponse(
        id=req.id,
        requester_id=req.requester_id,
        requester_name=req.requester.name,
        requester_email=req.requester.email,
        document_id=req.document_id,
        document_name=req.document.name,
        requested_sections=req.requested_sections,
        justification=req.justification,
        status=req.status,
        created_at=req.created_at,
        updated_at=req.updated_at
    )

@router.post("/request", response_model=AccessRequestResponse, status_code=status.HTTP_201_CREATED)
def create_override_request(
    payload: AccessRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits a new document/section clearance override request.
    Validates permissions via PolicyEngine.
    """
    # Auto run expiration sweep first
    AccessControlService.expire_overrides(db)
    
    req = AccessControlService.create_request(
        db=db,
        requester=current_user,
        document_id=payload.document_id,
        requested_sections=payload.requested_sections,
        justification=payload.justification
    )
    return map_request_to_response(req)

@router.get("/requests", response_model=AccessRequestListResponse)
def list_override_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Queries override requests.
    Compliance officers see all tickets; standard users only see their own requests.
    """
    # Sweep expired grants
    AccessControlService.expire_overrides(db)

    # Determine if approver (has 'audit' permission)
    is_approver = "audit" in current_user.role.permissions
    
    if is_approver:
        requests = AccessControlService.list_all_requests(db)
    else:
        stmt = select(AccessRequest).where(
            AccessRequest.requester_id == current_user.id
        ).order_by(AccessRequest.created_at.desc())
        requests = list(db.scalars(stmt).all())
        
    return AccessRequestListResponse(
        requests=[map_request_to_response(r) for r in requests]
    )

@router.get("/request/{id}", response_model=AccessRequestResponse)
def get_override_request_details(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetches details of a single override request.
    """
    req = AccessControlService.get_request(db, id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Override request not found."
        )
        
    # Security: check ownership or reviewer credentials
    is_owner = req.requester_id == current_user.id
    is_approver = "audit" in current_user.role.permissions
    
    if not (is_owner or is_approver):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You are not authorized to view this request details."
        )
        
    return map_request_to_response(req)

@router.post("/request/{id}/approve", response_model=AccessRequestResponse)
def approve_override_request(
    id: int,
    review: AccessRequestReview,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approves a pending override request, creating active temporary access grants.
    """
    req = AccessControlService.approve_request(
        db=db,
        reviewer=current_user,
        request_id=id,
        remarks=review.remarks,
        valid_hours=review.valid_hours or 24
    )
    return map_request_to_response(req)

@router.post("/request/{id}/reject", response_model=AccessRequestResponse)
def reject_override_request(
    id: int,
    review: AccessRequestReview,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rejects a pending override request.
    """
    req = AccessControlService.reject_request(
        db=db,
        reviewer=current_user,
        request_id=id,
        remarks=review.remarks
    )
    return map_request_to_response(req)

@router.post("/request/{id}/cancel", response_model=AccessRequestResponse)
def cancel_override_request(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancels a pending override request before it undergoes review.
    """
    req = AccessControlService.cancel_request(
        db=db,
        requester=current_user,
        request_id=id
    )
    return map_request_to_response(req)
