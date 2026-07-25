"""
Recommendation generation wrapper for plant diagnostic actions.
"""
from typing import List, Dict, Any


def generate_actionable_recommendations(analysis_context: Dict[str, Any]) -> List[str]:
    """Extract actionable maintenance and safety recommendations from diagnostic context."""
    recommendations = []
    if "anomalies" in analysis_context:
        recommendations.append("Inspect vibration sensors and bearing lubrications immediately.")
    if "compliance_risk" in analysis_context:
        recommendations.append("Verify ISO 50001 compliance logs for equipment operating limits.")
    
    if not recommendations:
        recommendations.append("Perform routine operational parameter checks.")

    return recommendations
