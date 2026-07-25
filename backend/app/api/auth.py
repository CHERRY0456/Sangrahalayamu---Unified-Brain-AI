from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.auth import UserLoginRequest, TokenRefreshRequest, TokenResponse, UserMeResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.core.config import settings
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

def _set_auth_cookies(response: Response, tokens: TokenResponse):
    """Helper to set authentication cookies securely."""
    secure_cookie = settings.app.env.value == "production"
    is_dev = settings.app.env.value == "development"

    # In development/localhost, omit max_age (set to None) so cookies become true Session Cookies.
    # Browsers delete session cookies automatically when the browser session/process closes.
    access_max_age = None if is_dev else 3600
    refresh_max_age = None if is_dev else 86400 * 7
    session_max_age = None if is_dev else 3600

    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=access_max_age
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=refresh_max_age
    )
    response.set_cookie(
        key="ib-session-token",
        value="authenticated",
        httponly=False,
        secure=secure_cookie,
        samesite="lax",
        max_age=session_max_age
    )

@router.post("/login", response_model=dict)
def login(login_data: UserLoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    Authenticates email & password credentials, setting signed access and refresh tokens as cookies and JSON payload.
    """
    tokens = AuthService.authenticate_user(db, login_data)
    _set_auth_cookies(response, tokens)
    return {
        "message": "Login successful",
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=dict)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Validates current active refresh token from cookies to rotate credentials and issue new cookies.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Refresh token missing")

    tokens = AuthService.rotate_tokens(db, refresh_token)
    _set_auth_cookies(response, tokens)
    return {"message": "Tokens refreshed successfully"}

@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Logs out the session, revoking/invalidating the active refresh token and clearing cookies.
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        AuthService.logout(db, refresh_token)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("ib-session-token")
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
