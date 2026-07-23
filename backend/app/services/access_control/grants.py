from datetime import datetime, timezone, timedelta
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.access_grant import AccessGrant
from app.models.access_request import AccessRequest
from .history import AccessControlHistory

class AccessGrantsManager:
    @staticmethod
    def create_grant(
        db: Session, 
        request_id: int, 
        user_id: int, 
        document_id: int, 
        allowed_sections: List[str], 
        valid_hours: int,
        granted_by: int
    ) -> AccessGrant:
        """
        Creates a new temporary grant matching request ticket.
        """
        expires_at = datetime.utcnow() + timedelta(hours=valid_hours)
        
        grant = AccessGrant(
            request_id=request_id,
            user_id=user_id,
            document_id=document_id,
            allowed_sections=allowed_sections,
            expires_at=expires_at,
            granted_by=granted_by
        )
        db.add(grant)
        db.commit()
        db.refresh(grant)
        return grant

    @staticmethod
    def get_active_grant_sections(db: Session, user_id: int, document_id: int) -> List[str]:
        """
        Queries and returns sections currently unlocked by active approved overrides.
        """
        now = datetime.utcnow()
        stmt = select(AccessGrant).where(
            AccessGrant.user_id == user_id,
            AccessGrant.document_id == document_id,
            AccessGrant.expires_at > now
        )
        grants = db.scalars(stmt).all()
        
        sections = []
        for g in grants:
            sections.extend(g.allowed_sections)
            
        return list(set(sections))  # Remove duplicates

    @staticmethod
    def has_active_override(db: Session, user_id: int, document_id: int, section_name: str = None) -> bool:
        """
        Returns boolean if user contains active overrides for the document scope.
        """
        active_sections = AccessGrantsManager.get_active_grant_sections(db, user_id, document_id)
        if not active_sections:
            return False
            
        # If grant covers "Entire Document", all sections are unlocked
        if "Entire Document" in active_sections:
            return True
            
        if not section_name:
            return len(active_sections) > 0
            
        return section_name in active_sections

    @staticmethod
    def expire_overrides(db: Session) -> int:
        """
        Identifies elapsed grants, updates parent requests status to 'Expired' and records history logs.
        """
        now = datetime.utcnow()
        
        # Select active requests that are linked to expired grants but still marked 'Approved'
        stmt = select(AccessRequest).join(AccessGrant).where(
            AccessRequest.status == "Approved",
            AccessGrant.expires_at < now
        )
        expired_requests = db.scalars(stmt).all()
        
        expired_count = 0
        for req in expired_requests:
            req.status = "Expired"
            
            # Log event in history
            grant = req.grant[0] if req.grant else None
            grantor_id = grant.granted_by if grant else req.requester_id
            
            AccessControlHistory.log_action(
                db=db,
                request_id=req.id,
                actor_id=grantor_id,
                action="expire",
                remarks="Temporary clearance grant period elapsed."
            )
            expired_count += 1
            
        if expired_count > 0:
            db.commit()
            
        return expired_count
