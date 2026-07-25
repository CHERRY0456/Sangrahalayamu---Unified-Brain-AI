"""
Retrieval result reranker implementation.
"""
from typing import List
from .models import RetrievalMatch


class ResultReranker:
    def rerank(self, matches: List[RetrievalMatch]) -> List[RetrievalMatch]:
        """Rerank matches based on combined vector and graph confidence scores."""
        return sorted(matches, key=lambda m: m.score, reverse=True)


result_reranker = ResultReranker()
