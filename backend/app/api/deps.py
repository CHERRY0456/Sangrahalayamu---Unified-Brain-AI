from typing import Generator, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database.session import get_db
from app.models.user import User
from app.services.auth.jwt import JwtService
from app.services.policy import PolicyEngine

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency verifying signed JWT access token signature from cookies, mapping payload subject to User model.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Access token cookie missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = JwtService.verify_token(token, is_refresh=False)

    stmt = select(User).where(User.id == user_id)
    user = db.scalar(stmt)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User identity not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

class PermissionChecker:
    """
    RBAC Route Guard checking if the authenticated identity contains the required permission tag.
    Consumes permissions checked by the PolicyEngine.
    """
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        # Resolve specific action evaluation based on permissions
        user_permissions = current_user.role.permissions
        if self.required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: Insufficient permissions configuration clearance for '{self.required_permission}'."
            )
        return current_user

class PolicyUploadGuard:
    """
    FastAPI Route Guard checking upload action authorization via PolicyEngine.
    """
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        decision = PolicyEngine.evaluate_upload_action(current_user)
        if not decision.allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=decision.reason
            )
        return current_user

class PolicyAuditGuard:
    """
    FastAPI Route Guard checking audit logs view action authorization via PolicyEngine.
    """
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        decision = PolicyEngine.evaluate_audit_view_action(current_user)
        if not decision.allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=decision.reason
            )
        return current_user
