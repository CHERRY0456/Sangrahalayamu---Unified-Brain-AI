from typing import List, Dict, Any
from app.models.audit_log import AuditLog

class ServiceStatisticsAggregator:
    @staticmethod
    def compile(logs: List[AuditLog]) -> Dict[str, Any]:
        """
        Compiles summaries: category splits, last activity, and frequent services.
        """
        if not logs:
            return {
                "total_events": 0,
                "event_categories": {},
                "last_activity": "No recent activity",
                "frequent_service": "None"
            }

        categories = {}
        services = {}
        last_act = logs[0].timestamp.isoformat()

        for log in logs:
            categories[log.event_type] = categories.get(log.event_type, 0) + 1
            services[log.source_service] = services.get(log.source_service, 0) + 1

        # Find most frequent service
        frequent = max(services.items(), key=lambda x: x[1])[0] if services else "None"

        return {
            "total_events": len(logs),
            "event_categories": categories,
            "last_activity": last_act,
            "frequent_service": frequent
        }
