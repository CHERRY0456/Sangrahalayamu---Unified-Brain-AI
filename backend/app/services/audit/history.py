from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.audit_log import AuditLog
from .models import HistoryTimeline, UserActivityEvent
from .statistics import ServiceStatisticsAggregator
from .filters import AuditFilterBuilder

class UserActivityHistoryCompiler:
    @staticmethod
    def compile_timeline(db: Session, user: User, limit: int = 50) -> HistoryTimeline:
        """
        Compiles user-centric activity history from raw immutable audit logs.
        Matches human-readable actions: 'Logged in', 'Uploaded document', etc. (Ticket #11 constraint).
        """
        # Build query for target actor_id
        stmt = AuditFilterBuilder.build_query(actor_id=user.id)
        stmt = stmt.limit(limit)
        logs = db.scalars(stmt).all()

        timeline_events = []
        for log in logs:
            desc = UserActivityHistoryCompiler._map_action_description(log)
            timeline_events.append(UserActivityEvent(
                timestamp=log.timestamp,
                activity_description=desc,
                service=log.source_service,
                status=log.status,
                request_id=log.request_id
            ))

        # Compile summaries and category statistics
        stats = ServiceStatisticsAggregator.compile(logs)
        
        last_act = stats.get("last_activity", "No recent activity")
        summary_text = (
            f"User '{user.email}' has recorded {len(timeline_events)} total events in this session. "
            f"Last active on {last_act} using service '{stats.get('frequent_service', 'None')}'."
        )

        return HistoryTimeline(
            user_id=user.id,
            user_email=user.email,
            events=timeline_events,
            summary=summary_text,
            statistics=stats
        )

    @staticmethod
    def _map_action_description(log: AuditLog) -> str:
        etype = log.event_type.lower()
        act = log.action.lower()
        
        if "authentication" in etype:
            return "Logged in"
        elif "upload" in etype:
            return "Uploaded document"
        elif "processing" in etype:
            return "Processed document metadata"
        elif "retrieval" in etype:
            return "Searched database chunks"
        elif "generation" in etype or "ai" in etype:
            return "Asked question"
        elif "override" in etype:
            if "approve" in act:
                return "Access approved"
            return "Requested access"
        elif "download" in etype:
            return "Downloaded document"
        elif "recommendation" in etype:
            return "Received AI recommendation"
            
        return f"Performed action '{log.action}'"
