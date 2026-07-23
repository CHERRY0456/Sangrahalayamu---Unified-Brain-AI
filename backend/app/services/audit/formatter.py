from .models import HistoryTimeline

class HistoryTimelineFormatter:
    @staticmethod
    def to_markdown(timeline: HistoryTimeline) -> str:
        """
        Formats user timelines into structured markdown tables.
        """
        md = []
        md.append(f"# User Activity Timeline Audit")
        md.append(f"- **User**: {timeline.user_email} (ID: {timeline.user_id})")
        md.append(f"- **Summary**: {timeline.summary}")
        
        # Stats
        stats = timeline.statistics
        md.append(f"\n### 📊 Activity statistics")
        md.append(f"- **Total recorded actions**: {stats.get('total_events', 0)}")
        md.append(f"- **Most active service**: `{stats.get('frequent_service', 'None')}`")
        
        md.append(f"\n### 🕒 Chronological Log Trail")
        md.append("| Timestamp | Service | Action description | Status | Request correlation ID |")
        md.append("|---|---|---|---|---|")
        
        if not timeline.events:
            md.append("| N/A | None | No activity records found. | N/A | N/A |")
        else:
            for ev in timeline.events:
                req_id = ev.request_id if ev.request_id else "N/A"
                md.append(
                    f"| {ev.timestamp.isoformat()} | {ev.service} | "
                    f"{ev.activity_description} | {ev.status} | `{req_id}` |"
                )
                
        return "\n".join(md)
