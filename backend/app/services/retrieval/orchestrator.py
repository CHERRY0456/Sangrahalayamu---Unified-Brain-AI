import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.document import Document
from .models import (
    RetrievalFilters,
    RetrievedChunkContext,
    GraphContext,
    HybridRetrievalPackage,
    ContextPackage
)
from .metadata import MetadataFilter
from .provider_factory import RetrievalProviderFactory
from .permissions import RetrievalPermissionFilter
from .fusion import RetrievalRankFusion
from .context_builder import context_builder

logger = logging.getLogger("sangrahalayamu.retrieval.orchestrator")

class HybridRetrievalService:
    """
    Instance-based Hybrid Retrieval Orchestrator coordinating SQL metadata filtering,
    semantic search, graph traversal, and PolicyEngine permissions.
    """
    def __init__(self):
        self.vector_provider = RetrievalProviderFactory.get_vector_provider()
        self.graph_provider = RetrievalProviderFactory.get_graph_provider()

    def retrieve(
        self,
        db: Session,
        query: str,
        user: User,
        filters: Optional[RetrievalFilters] = None,
        limit: int = 4
    ) -> ContextPackage:
        """
        Coordinates hybrid retrieval operations and returns a permission-aware context package.
        """
        logger.info(
            f"Retrieval Request: User '{user.email}' (Role: {user.role.name}) | Query: '{query}'"
        )

        # 1. Candidate Pre-filtering (PostgreSQL/SQLite metadata checks)
        candidate_ids = MetadataFilter.filter_candidates(db, filters)
        if not candidate_ids:
            return context_builder.build_context(HybridRetrievalPackage(
                query=query,
                chunks=[],
                graph_relationships=[],
                metadata_summary={"candidate_documents_count": 0},
                explanation="No candidates matched the specified metadata filters."
            ))

        # 2. Semantic Search candidate chunks (Raw vector search mock)
        semantic_res = self.vector_provider.search(
            db=db,
            query=query,
            limit=limit * 3,  # Fetch extra candidates to account for permissions drops
            candidate_doc_ids=candidate_ids
        )

        # 3. Graph Search candidate chunks (Graph relations mock)
        graph_res = self.graph_provider.search_graph(
            db=db,
            query=query,
            limit=limit * 3,
            candidate_doc_ids=candidate_ids
        )

        # 4. Permission filtering check (PolicyEngine clearances and overrides)
        # Filters semantic and graph candidates dynamically before ranking
        original_semantic_count = len(semantic_res.matches)
        original_graph_count = len(graph_res.matches)

        authorized_semantic_matches = RetrievalPermissionFilter.filter_authorized_chunks(
            db=db,
            user=user,
            matches=semantic_res.matches
        )
        
        authorized_graph_matches = RetrievalPermissionFilter.filter_authorized_chunks(
            db=db,
            user=user,
            matches=graph_res.matches
        )

        # Calculate count filtered by permissions
        filtered_sem_count = original_semantic_count - len(authorized_semantic_matches)
        filtered_graph_count = original_graph_count - len(authorized_graph_matches)
        total_permissions_filtered = filtered_sem_count + filtered_graph_count

        # Update provider results with authorized collections
        semantic_res.matches = authorized_semantic_matches
        graph_res.matches = authorized_graph_matches

        # 5. Hybrid Rank Fusion (Normalized min-max weights calculation)
        fused_rankings = RetrievalRankFusion.fuse_results(
            semantic_res=semantic_res,
            graph_res=graph_res,
            limit=limit
        )

        # 6. Gather context details (chunks text, hierarchy, pages)
        retrieved_chunks: List[RetrievedChunkContext] = []
        
        # Build map of matching metadata details (avoid overwriting rich semantic metadata with sparser graph metadata)
        match_meta_map = {}
        for m in semantic_res.matches:
            match_meta_map[m.chunk_id] = m.metadata
        for m in graph_res.matches:
            if m.chunk_id not in match_meta_map:
                match_meta_map[m.chunk_id] = m.metadata
            else:
                # Merge keys, ensuring we keep the 'text' key if it exists
                match_meta_map[m.chunk_id] = {**m.metadata, **match_meta_map[m.chunk_id]}

        for rank_idx, (chunk_id, score, explanation) in enumerate(fused_rankings):
            meta = match_meta_map.get(chunk_id, {})
            retrieved_chunks.append(RetrievedChunkContext(
                chunk_id=chunk_id,
                document_id=meta.get("document_id", 0),
                document_name=meta.get("document_name", "Unknown File"),
                section=meta.get("section", "Introduction"),
                text=meta.get("text", ""),
                page_numbers=meta.get("page_numbers", [1]),
                score=score,
                rank_explanation=explanation
            ))

        # 7. Unpack matching graph relationship edges
        relationships_list: List[GraphContext] = []
        raw_relations = graph_res.diagnostics.get("relationships", [])
        for rel in raw_relations:
            relationships_list.append(GraphContext(
                source=rel.get("source"),
                target=rel.get("target"),
                relationship_type=rel.get("relationship_type"),
                metadata=rel.get("metadata", {})
            ))

        # Compile summaries
        summary = {
            "query_terms_count": len(query.split()),
            "prefiltered_candidates": len(candidate_ids),
            "semantic_provider": semantic_res.provider_name,
            "graph_provider": graph_res.provider_name,
            "returned_chunks": len(retrieved_chunks),
            "graph_edges_count": len(relationships_list)
        }

        # Compile optional debugging diagnostics (Ticket #7 constraint)
        from app.core.config import settings
        diagnostics_data = None
        if settings.flags.enable_transparency:
            diagnostics_data = {
                "metadata_candidates_count": len(candidate_ids),
                "semantic_matches_considered": original_semantic_count,
                "graph_matches_considered": original_graph_count,
                "graph_relations_traversed": graph_res.diagnostics.get("total_edges_searched", 0),
                "fusion_weights_applied": {
                    "semantic": settings.retrieval.weight_semantic,
                    "graph": settings.retrieval.weight_graph,
                    "metadata": settings.retrieval.weight_metadata
                },
                "matches_filtered_by_permissions": total_permissions_filtered
            }

        package = HybridRetrievalPackage(
            query=query,
            chunks=retrieved_chunks,
            graph_relationships=relationships_list,
            metadata_summary=summary,
            explanation=(
                f"Retrieved {len(retrieved_chunks)} relevant chunks pre-filtered by metadata, "
                f"ranked using hybrid weights (0.60 semantic / 0.25 graph / 0.15 metadata) and protected "
                f"by Policy Engine security clearance guards."
            ),
            diagnostics=diagnostics_data
        )

        # Emit retrieval audit event (Ticket #11 constraint)
        try:
            from app.services.audit import audit_service, AuditEvent, EVENT_TYPE_RETRIEVAL
            audit_service.record_event(db, AuditEvent(
                event_type=EVENT_TYPE_RETRIEVAL,
                actor_id=user.id,
                actor_role=user.role.name if user.role else "User",
                action="retrieve",
                status="SUCCESS",
                source_service="retrieval_engine",
                metadata={"query": query, "chunks_returned": len(retrieved_chunks)}
            ))
        except Exception:
            pass

        return context_builder.build_context(package)

# Expose global instance for controller and pipeline imports
hybrid_retrieval_service = HybridRetrievalService()
