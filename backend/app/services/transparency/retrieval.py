from typing import Dict, Any
from app.services.retrieval.models import HybridRetrievalPackage
from .models import RetrievalSummary

class RetrievalExplanationEngine:
    @staticmethod
    def generate(retrieval_package: HybridRetrievalPackage) -> RetrievalSummary:
        summary = retrieval_package.metadata_summary
        diagnostics = retrieval_package.diagnostics or {}

        weights = diagnostics.get("fusion_weights_applied", {
            "semantic": 0.60,
            "graph": 0.25,
            "metadata": 0.15
        })

        cand_count = summary.get("prefiltered_candidates", 0)
        chunks_count = len(retrieval_package.chunks)
        edges_count = summary.get("graph_edges_count", 0)

        desc = (
            f"Retrieved {chunks_count} relevant chunks from {cand_count} candidate documents "
            f"matching pre-filtering constraints. Hybrid fusion weights applied: "
            f"Semantic vector Jaccard similarity ({int(weights.get('semantic', 0.6)*100)}%), "
            f"Graph connection traversal ({int(weights.get('graph', 0.25)*100)}%), "
            f"and metadata pre-filtering properties ({int(weights.get('metadata', 0.15)*100)}%)."
        )

        return RetrievalSummary(
            num_documents_considered=cand_count,
            metadata_filters_applied={"status": "PROCESSED", "is_active": True},
            num_semantic_matches=diagnostics.get("semantic_matches_considered", chunks_count),
            num_graph_relations_expanded=diagnostics.get("graph_relations_traversed", edges_count),
            fusion_weights=weights,
            description=desc,
            provenance="retrieval_engine"
        )
