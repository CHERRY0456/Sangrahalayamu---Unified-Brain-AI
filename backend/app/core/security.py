from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.core.config import settings

password_hasher = PasswordHasher()

def hash_password(password: str) -> str:
    """
    Hashes a password string using Argon2.
    """
    return password_hasher.hash(password)

def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    Verifies a plain password against an Argon2 hash.
    """
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a signed access token.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.app.access_token_expire_minutes)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access"
    }
    encoded_jwt = jwt.encode(to_encode, settings.app.secret_key, algorithm="HS256")
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a signed refresh token.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.app.refresh_token_expire_days)
        
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(to_encode, settings.app.jwt_secret_key, algorithm="HS256")
    return encoded_jwt

def decode_token(token: str, is_refresh: bool = False) -> Optional[dict]:
    """
    Decodes and validates a signed JWT token.
    """
    key = settings.app.jwt_secret_key if is_refresh else settings.app.secret_key
    try:
        payload = jwt.decode(token, key, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
