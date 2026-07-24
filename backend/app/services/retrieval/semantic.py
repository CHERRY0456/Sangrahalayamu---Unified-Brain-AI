import re
from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.document import Document
from .models import RetrievalProviderResult, RetrievalMatch
from app.services.embeddings.embedding_service import embedding_service
from app.services.qdrant.qdrant_service import qdrant_service

class VectorRetrievalProvider(ABC):
    @abstractmethod
    def search(
        self,
        db: Session,
        query: str,
        limit: int,
        candidate_doc_ids: List[int]
    ) -> RetrievalProviderResult:
        """
        Executes semantic vector retrieval return standardized results wrapper.
        """
        pass

class QdrantVectorRetrievalProvider(VectorRetrievalProvider):
    """
    Production vector retrieval using Qdrant and the Embedding Service.
    """
    def search(
        self,
        db: Session,
        query: str,
        limit: int,
        candidate_doc_ids: List[int]
    ) -> RetrievalProviderResult:

        # 1. Embed the query
        try:
            query_embedding = embedding_service.embed_text(query)
        except Exception as e:
            # Fallback to empty if embedding fails
            return RetrievalProviderResult(matches=[], provider_name="QdrantVectorEngine")

        # 2. Search Qdrant
        # Note: We must stringify the candidate doc IDs because Qdrant payload stores them as strings
        str_candidates = [str(doc_id) for doc_id in candidate_doc_ids] if candidate_doc_ids else None

        results = qdrant_service.search(
            query_embedding=query_embedding,
            candidate_doc_ids=str_candidates,
            limit=limit
        )

        # 3. Map Qdrant results to internal RetrievalMatch schema
        matches = []
        for r in results:
            matches.append(RetrievalMatch(
                chunk_id=r.chunk_id,
                score=round(r.score, 4),
                metadata=r.payload.metadata
            ))

        return RetrievalProviderResult(
            matches=matches,
            provider_name="QdrantVectorEngine",
            diagnostics={
                "candidate_documents_searched": len(candidate_doc_ids) if candidate_doc_ids else 0,
                "total_chunks_evaluated": len(matches),
                "qdrant_latency": getattr(query_embedding, "latency", 0)
            }
        )
