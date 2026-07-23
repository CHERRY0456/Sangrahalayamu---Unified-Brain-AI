from datetime import datetime
from sqlalchemy.orm import Session
from app.models.approval_history import ApprovalHistory

class AccessControlHistory:
    @staticmethod
    def log_action(
        db: Session, 
        request_id: int, 
        actor_id: int, 
        action: str, 
        remarks: str = None
    ) -> ApprovalHistory:
        """
        Logs a workflow transition audit record inside the database history tables.
        """
        log_entry = ApprovalHistory(
            request_id=request_id,
            actor_id=actor_id,
            action=action,
            remarks=remarks,
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
