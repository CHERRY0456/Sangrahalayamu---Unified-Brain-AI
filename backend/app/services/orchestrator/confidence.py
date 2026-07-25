"""
Confidence metric calculator for RAG and agent responses.
"""
from typing import List, Dict, Any


def calculate_confidence_score(retrieved_chunks: List[Dict[str, Any]], reasoning_steps: List[str]) -> float:
    """Compute overall confidence score based on retrieval relevance and reasoning chain."""
    if not retrieved_chunks:
        return 0.5

    scores = [chunk.get("score", 0.7) for chunk in retrieved_chunks]
    avg_vector_score = sum(scores) / len(scores) if scores else 0.7

    reasoning_bonus = min(len(reasoning_steps) * 0.05, 0.15)
    final_score = min(max(avg_vector_score + reasoning_bonus, 0.0), 1.0)
    return round(final_score, 2)
