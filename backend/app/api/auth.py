from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.auth import UserLoginRequest, TokenRefreshRequest, TokenResponse, UserMeResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates email & password credentials, returning signed access and refresh tokens.
    """
    return AuthService.authenticate_user(db, login_data)

@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_data: TokenRefreshRequest, db: Session = Depends(get_db)):
    """
    Validates current active refresh token to rotate credentials and issue new tokens.
    """
    return AuthService.rotate_tokens(db, refresh_data.refresh_token)

@router.post("/logout")
def logout(refresh_data: TokenRefreshRequest, db: Session = Depends(get_db)):
    """
    Logs out the session, revoking/invalidating the active refresh token.
    """
    AuthService.logout(db, refresh_data.refresh_token)
    return {"message": "Session successfully invalidated."}

@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Resolves logged-in identity profile metadata, permissions, and workspace manifest configs.
    """
    return AuthService.get_current_user_me(db, current_user.id)

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Initiates password reset flow. Generates a reset token and stores it.
    Always returns success to prevent email enumeration.
    """
    return AuthService.forgot_password(db, payload.email)

@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Validates a password reset token and updates the user's password.
    Revokes all existing sessions for security.
    """
    return AuthService.reset_password(db, payload.token, payload.new_password)

