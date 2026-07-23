from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.config import settings

class JwtService:
    @staticmethod
    def generate_token_pair(user_id: int) -> tuple[str, str]:
        """
        Creates access and refresh tokens.
        """
        access_token = create_access_token(subject=str(user_id))
        refresh_token = create_refresh_token(subject=str(user_id))
        return access_token, refresh_token

    @staticmethod
    def verify_token(token: str, is_refresh: bool = False) -> int:
        """
        Verifies signed token and extracts the subject (user_id).
        Raises credentials exception if verification fails.
        """
        payload = decode_token(token, is_refresh=is_refresh)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_type = payload.get("type")
        expected_type = "refresh" if is_refresh else "access"
        if token_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {expected_type} token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        subject = payload.get("sub")
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload is missing subject.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            return int(subject)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token subject parameter must be a valid user identifier integer.",
                headers={"WWW-Authenticate": "Bearer"},
            )
