import uuid
import logging
from typing import List, Dict, Any, Optional

from qdrant_client.http import models as qmodels
from .repositories.vector_repository import VectorRepository
from .schemas.vector_models import QdrantPayload, SearchResult
from app.services.embeddings.schemas.embedding_models import EmbeddingVector
from app.core.config import settings

logger = logging.getLogger(__name__)

class QdrantService:
    """
    Service layer providing embedding ingestion and retrieval abstractions.
    Maps domain models to Qdrant models.
    """
    def __init__(self):
        self.repo = VectorRepository()
        
    def initialize(self):
        """Called during application startup to ensure collections exist."""
        self.repo.validate_collection()

    def health_check(self) -> bool:
        return self.repo.health_check()

    def upsert_document_chunks(self, document_id: str, workspace_id: str, role_permissions: List[str], chunks: List[Dict[str, Any]], embeddings: List[EmbeddingVector]):
        """
        Takes raw chunks and their corresponding embeddings and upserts them.
        chunks: List of dicts, expected to have 'text', 'metadata', 'entities', 'relationships', 'chunk_id', 'provenance'
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatched chunks length ({len(chunks)}) and embeddings length ({len(embeddings)})")

        points = []
        for i, chunk in enumerate(chunks):
            # Generate UUID if chunk_id not present or not UUID formatted (Qdrant requires UUID or Int)
            raw_chunk_id = chunk.get("chunk_id", str(uuid.uuid4()))
            # We map the raw ID into the payload, but generate a predictable UUID for Qdrant ID if needed
            # For simplicity, let's assume `raw_chunk_id` can be converted to UUID, or we just hash it.
            qdrant_id = str(uuid.uuid5(uuid.NAMESPACE_OID, raw_chunk_id))
            
            payload = QdrantPayload(
                chunk_id=raw_chunk_id,
                document_id=document_id,
                workspace_id=workspace_id,
                role_permissions=role_permissions,
                metadata=chunk.get("metadata", {}),
                provenance=chunk.get("provenance", {}),
                entities=chunk.get("entities", []),
                relationships=chunk.get("relationships", [])
            )
            
            # Embed text content directly into the metadata for retrieval context
            payload.metadata["text"] = chunk.get("text", "")

            point = qmodels.PointStruct(
                id=qdrant_id,
                vector=embeddings[i].vector,
                payload=payload.model_dump()
            )
            points.append(point)

        if points:
            self.repo.upsert_batch(points)
            logger.info(f"Upserted {len(points)} vector chunks for document {document_id}")

    def delete_document(self, document_id: str):
        self.repo.delete_by_document(document_id)
        logger.info(f"Deleted vectors for document {document_id}")

    def search(
        self, 
        query_embedding: EmbeddingVector, 
        workspace_id: Optional[str] = None,
        role_permissions: Optional[List[str]] = None,
        candidate_doc_ids: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Search for similar vectors, applying required workspace and role permission filters if provided.
        """
        filter_conditions = []
        
        if workspace_id:
            filter_conditions.append(
                qmodels.FieldCondition(
                    key="workspace_id",
                    match=qmodels.MatchValue(value=workspace_id)
                )
            )
            
        if candidate_doc_ids:
            filter_conditions.append(
                qmodels.FieldCondition(
                    key="document_id",
                    match=qmodels.MatchAny(any=candidate_doc_ids)
                )
            )

        # Role permission filtering: Must match at least one of the user's roles if restricted
        if role_permissions:
            filter_conditions.append(
                qmodels.FieldCondition(
                    key="role_permissions",
                    match=qmodels.MatchAny(any=role_permissions)
                )
            )

        qdrant_results = self.repo.search(
            query_vector=query_embedding.vector,
            filter_conditions=filter_conditions,
            limit=limit,
            score_threshold=settings.retrieval.min_similarity_score
        )

        results = []
        for r in qdrant_results:
            try:
                raw_payload = getattr(r, "payload", {}) or (r.get("payload", {}) if isinstance(r, dict) else {})
                score = getattr(r, "score", 0.0) if hasattr(r, "score") else (r.get("score", 0.0) if isinstance(r, dict) else 0.0)
                
                payload = QdrantPayload(**raw_payload)
                results.append(
                    SearchResult(
                        chunk_id=payload.chunk_id,
                        score=score,
                        payload=payload
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to parse payload for vector point: {e}")
                
        return results

    def get_stats(self) -> Dict[str, Any]:
        return self.repo.get_collection_statistics()

qdrant_service = QdrantService()
