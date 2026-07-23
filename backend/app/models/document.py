from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.postgres import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)
    classification: Mapped[str] = mapped_column(String(50), nullable=False)  # Public, Internal, Confidential, Restricted, Executive
    required_clearance: Mapped[str] = mapped_column(String(50), nullable=False)  # LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_5
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="UPLOADED", nullable=False)  # UPLOADED, STORED, PROCESSING, INDEXED, READY
    
    # Optional JSON metadata store for future extensibility (avoids schema modifications)
    doc_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = relationship("User", backref="documents")
