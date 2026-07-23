from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.postgres import Base

class AccessGrant(Base):
    __tablename__ = "access_grants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("access_requests.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    # Allowed sections list (e.g. ["Section 2.3"] or ["Entire Document"])
    allowed_sections: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    granted_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    request = relationship("AccessRequest", back_populates="grant" if hasattr(Base, "_dummy") else None, backref="grant")
    user = relationship("User", foreign_keys=[user_id], backref="grants")
    grantor = relationship("User", foreign_keys=[granted_by], backref="issued_grants")
    document = relationship("Document", backref="grants")
