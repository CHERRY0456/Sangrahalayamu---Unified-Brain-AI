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

class MockVectorRetrievalProvider(VectorRetrievalProvider):
    """
    Mock vector search resolving document chunks and scoring Jaccard keyword overlap (0-1).
    """
    def search(
        self, 
        db: Session, 
        query: str, 
        limit: int, 
        candidate_doc_ids: List[int]
    ) -> RetrievalProviderResult:
        if not candidate_doc_ids:
            return RetrievalProviderResult(matches=[], provider_name="MockVectorEngine")

        # 1. Retrieve all candidate documents
        stmt = select(Document).where(Document.id.in_(candidate_doc_ids), Document.is_active == True)
        docs = db.scalars(stmt).all()

        # Extract tokens from query
        query_words = set(re.findall(r"\w+", query.lower()))
        
        matches = []
        for doc in docs:
            payload = doc.doc_metadata.get("processed_payload", {})
            chunks = payload.get("chunks", [])

            for ch in chunks:
                chunk_text = ch.get("text", "")
                chunk_words = set(re.findall(r"\w+", chunk_text.lower()))
                
                # Compute term Jaccard similarity score (inherently 0 to 1 range)
                intersection = query_words.intersection(chunk_words)
                union = query_words.union(chunk_words)
                
                # If query has no words, default score to 0.0
                jaccard_score = float(len(intersection)) / float(len(union)) if union else 0.0
                
                # Boost if exact matches occur on heading hierarchies
                headings = [h.lower() for h in ch.get("heading_hierarchy", [])]
                for heading in headings:
                    if any(qw in heading for qw in query_words):
                        jaccard_score = min(1.0, jaccard_score + 0.15)

                matches.append(RetrievalMatch(
                    chunk_id=ch.get("chunk_id"),
                    score=round(jaccard_score, 4),
                    metadata={
                        "document_id": doc.id,
                        "document_name": doc.name,
                        "section": ch.get("section", "Introduction"),
                        "text": chunk_text,
                        "page_numbers": ch.get("page_numbers", [1]),
                        "heading_hierarchy": ch.get("heading_hierarchy", [])
                    }
                ))

        # Sort matches by Jaccard score descending
        matches = sorted(matches, key=lambda m: m.score, reverse=True)
        top_matches = matches[:limit]

        return RetrievalProviderResult(
            matches=top_matches,
            provider_name="MockVectorEngine",
            diagnostics={
                "candidate_documents_searched": len(candidate_doc_ids),
                "total_chunks_evaluated": len(matches),
                "query_token_count": len(query_words)
            }
        )
