from typing import List, Dict, Any, Tuple
from app.core.config import settings
from .models import RetrievalProviderResult, RetrievalMatch, RetrievedChunkContext

class RetrievalRankFusion:
    """
    Standardizes and normalizes score ranges from Semantic and Graph providers,
    then executes weighted rank fusion calculations.
    """
    @staticmethod
    def fuse_results(
        semantic_res: RetrievalProviderResult,
        graph_res: RetrievalProviderResult,
        limit: int
    ) -> List[Tuple[str, float, str]]:
        """
        Merges results from providers by normalizing raw scores to a 0-1 range
        and applying configurable weights.
        Returns a list of tuples: (chunk_id, fused_score, explanation_text) sorted by score.
        """
        # Collect all unique chunk IDs
        all_chunk_ids = set()
        sem_raw_map: Dict[str, float] = {}
        graph_raw_map: Dict[str, float] = {}
        chunk_metadata_map: Dict[str, Dict[str, Any]] = {}

        for m in semantic_res.matches:
            all_chunk_ids.add(m.chunk_id)
            sem_raw_map[m.chunk_id] = m.score
            chunk_metadata_map[m.chunk_id] = m.metadata

        for m in graph_res.matches:
            all_chunk_ids.add(m.chunk_id)
            graph_raw_map[m.chunk_id] = m.score
            if m.chunk_id not in chunk_metadata_map:
                chunk_metadata_map[m.chunk_id] = m.metadata

        chunk_id_list = list(all_chunk_ids)
        if not chunk_id_list:
            return []

        # 1. Normalize individual score lists to a common 0-1 range (Ticket #7 constraint)
        sem_scores = [sem_raw_map.get(cid, 0.0) for cid in chunk_id_list]
        graph_scores = [graph_raw_map.get(cid, 0.0) for cid in chunk_id_list]

        norm_sem = RetrievalRankFusion._normalize_list(sem_scores)
        norm_graph = RetrievalRankFusion._normalize_list(graph_scores)

        # 2. Compute weighted scores
        w_sem = settings.retrieval.weight_semantic
        w_graph = settings.retrieval.weight_graph
        w_meta = settings.retrieval.weight_metadata

        fused_results: List[Tuple[str, float, str]] = []
        for idx, chunk_id in enumerate(chunk_id_list):
            s_norm = norm_sem[idx]
            g_norm = norm_graph[idx]
            m_norm = 1.0  # Base metadata match score (candidates passed initial SQL metadata pre-filters)

            fused_score = (w_sem * s_norm) + (w_graph * g_norm) + (w_meta * m_norm)
            fused_score = round(fused_score, 4)

            # Build explainable ranking message
            explanation = (
                f"Fused Score: {fused_score} "
                f"(Semantic: {s_norm} x {w_sem} + Graph Relevance: {g_norm} x {w_graph} + Metadata: {m_norm} x {w_meta})"
            )

            fused_results.append((chunk_id, fused_score, explanation))

        # Sort descending by fused score
        fused_results = sorted(fused_results, key=lambda x: x[1], reverse=True)
        return fused_results[:limit]

    @staticmethod
    def _normalize_list(scores: List[float]) -> List[float]:
        """
        Performs min-max scaling to compress numbers into a clean 0.0 - 1.0 range.
        """
        if not scores:
            return []
        min_val = min(scores)
        max_val = max(scores)
        
        if max_val == min_val:
            # Avoid division by zero. If all values are identical and greater than 0, normalize to 1.0
            return [1.0 if max_val > 0.0 else 0.0] * len(scores)
            
        return [(s - min_val) / (max_val - min_val) for s in scores]
