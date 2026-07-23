from .models import RecommendationPackage

class RecommendationFormatter:
    @staticmethod
    def to_markdown(package: RecommendationPackage) -> str:
        """
        Formats proactive recommendations into clear markdown checklists.
        """
        if not package.recommendations:
            return "No proactive recommendations available for current user context."
            
        md = []
        md.append("# Proactive Intelligence Recommendations")
        md.append("> Anticipating useful next actions based on active parameters and clearances.\n")

        for idx, rec in enumerate(package.recommendations):
            md.append(f"### {idx+1}. {rec.title}")
            md.append(f"- **Category**: `{rec.category}` | **Confidence**: `{rec.confidence:.2f}`")
            md.append(f"- **Reason Code**: `{rec.recommendation_reason_code}`")
            md.append(f"- **Reason**: {rec.explanation}")
            md.append(f"- **Sources**: {', '.join(rec.source_documents)}")
            md.append("")

        if package.warnings:
            md.append("### ⚠️ Alerts")
            for w in package.warnings:
                md.append(f"- {w}")

        return "\n".join(md)
