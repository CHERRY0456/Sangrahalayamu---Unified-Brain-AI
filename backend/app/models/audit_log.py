import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Index
from app.database.postgres import Base

class AuditLog(Base):
    """
    SQLAlchemy model representing the append-only, immutable enterprise audit event store.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    event_version = Column(String(10), default="1.0", nullable=False)  # Ticket #11 extension requirement
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    event_type = Column(String(50), nullable=False)
    actor_id = Column(Integer, nullable=True)
    actor_role = Column(String(50), nullable=True)
    session_id = Column(String(100), nullable=True)
    request_id = Column(String(100), nullable=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(100), nullable=True)
    action = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False, default="INFO")
    source_service = Column(String(50), nullable=False)
    metadata_json = Column(JSON, nullable=True)

# Generate database indexes (Ticket #11 constraints)
Index("ix_audit_logs_actor_id", AuditLog.actor_id)
Index("ix_audit_logs_event_type", AuditLog.event_type)
Index("ix_audit_logs_timestamp", AuditLog.timestamp)
Index("ix_audit_logs_request_id", AuditLog.request_id)
Index("ix_audit_logs_resource_id", AuditLog.resource_id)
