import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.session import UserSession
from app.core.config import settings

class SessionService:
    @staticmethod
    def _hash_token(token: str) -> str:
        """
        Hashes a refresh token string using SHA-256 for secure database storage.
        """
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def create_session(db: Session, user_id: int, refresh_token: str) -> UserSession:
        """
        Creates and stores a new refresh token tracking session.
        Stores the hashed version of the token.
        """
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.app.refresh_token_expire_days)
        hashed_token = SessionService._hash_token(refresh_token)
        
        session = UserSession(
            user_id=user_id,
            refresh_token=hashed_token,
            expires_at=expires_at,
            is_revoked=False
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def validate_session(db: Session, refresh_token: str) -> bool:
        """
        Verifies if a refresh token is active, matches register, and is not revoked/expired.
        Compares hashed values.
        """
        hashed_token = SessionService._hash_token(refresh_token)
        stmt = select(UserSession).where(
            UserSession.refresh_token == hashed_token,
            UserSession.is_revoked == False
        )
        session = db.scalar(stmt)
        if not session:
            return False
        
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            now = datetime.utcnow()
        else:
            now = datetime.now(timezone.utc)

        if expires_at < now:
            session.is_revoked = True
            db.commit()
            return False
            
        return True

    @staticmethod
    def revoke_session(db: Session, refresh_token: str) -> None:
        """
        Revokes a session by invalidating its refresh token (upon logout).
        """
        hashed_token = SessionService._hash_token(refresh_token)
        stmt = select(UserSession).where(UserSession.refresh_token == hashed_token)
        session = db.scalar(stmt)
        if session:
            session.is_revoked = True
            db.commit()

    @staticmethod
    def revoke_all_user_sessions(db: Session, user_id: int) -> None:
        """
        Forces logout across all devices for a given user.
        """
        stmt = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.is_revoked == False
        )
        sessions = db.scalars(stmt).all()
        for session in sessions:
            session.is_revoked = True
        db.commit()
