from typing import List, Any
from app.services.retrieval.models import HybridRetrievalPackage
from app.services.orchestrator.models import AIResponse
from .models import PermissionSummary

class SystemWarningEngine:
    @staticmethod
    def compile_warnings(
        ai_response: AIResponse,
        retrieval_package: HybridRetrievalPackage,
        permissions: PermissionSummary
    ) -> List[str]:
        warnings = []

        # 1. Limited documentation check
        if len(retrieval_package.chunks) < 2:
            warnings.append("LIMITED_DOCUMENTATION_AVAILABLE")

        # 2. Low semantic similarity check
        has_high_score = any(ch.score >= 0.50 for ch in retrieval_package.chunks)
        if not has_high_score and retrieval_package.chunks:
            warnings.append("LOW_SEMANTIC_SIMILARITY")

        # 3. No graph support
        if retrieval_package.metadata_summary.get("graph_edges_count", 0) == 0:
            warnings.append("NO_GRAPH_SUPPORT_FOUND")

        # 4. Override access indicator
        if permissions.temporary_override_status:
            warnings.append("OVERRIDE_ACCESS_USED")

        # 5. Validation attempts retries indicator
        meta = ai_response.generation_metadata
        if meta and meta.validation_attempts > 1:
            warnings.append("RESPONSE_GENERATED_AFTER_RETRY")

        # 6. Fallback applied
        if ai_response.confidence == 0.0 or "HALLUCINATION_DETECTED" in ai_response.warnings:
            warnings.append("VALIDATION_FALLBACK_APPLIED")

        return warnings
