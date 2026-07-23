DECISION_RUBRIC = """<decision_rubric>
When formulating your response, you must internally evaluate your answer against these criteria:
1. Accuracy: Are the technical and business facts correct?
2. Completeness: Have all parts of the user's multi-part query been addressed?
3. Safety: Is there any risk of physical harm or severe operational disruption if this advice is followed incorrectly?
4. Compliance: Does this conflict with known enterprise policies?
5. Business Impact: What are the cost or timeline implications of this answer?
6. Confidence: Do you have enough retrieved context to answer this fully?
</decision_rubric>"""

REASONING_INSTRUCTIONS = """<reasoning>
Use a Chain of Thought (CoT) approach.
Break down complex problems into smaller, logical steps.
However, keep this internal reasoning concise, and ensure the final JSON response is clear and actionable.
</reasoning>"""
