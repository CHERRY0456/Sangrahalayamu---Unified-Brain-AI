from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.postgres import Base

class AccessRequest(Base):
    __tablename__ = "access_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    # Store requested sections (e.g. ["Section 2.3", "Section 5.1"])
    requested_sections: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    justification: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Pending", nullable=False)  # Pending, Approved, Rejected, Cancelled, Expired
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    requester = relationship("User", backref="access_requests")
    document = relationship("Document", backref="access_requests")
