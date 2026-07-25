"""
Graph and document evidence collector for response transparency.
"""
from typing import List, Dict, Any


class EvidenceCollector:
    def collect_evidence(self, graph_nodes: List[Dict[str, Any]], vector_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate topological graph evidence and text vector evidence into structured proof."""
        return {
            "graph_evidence": graph_nodes,
            "text_evidence": vector_chunks,
            "total_sources": len(graph_nodes) + len(vector_chunks)
        }


evidence_collector = EvidenceCollector()
