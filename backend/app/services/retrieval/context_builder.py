import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set
from .models import RetrievedChunkContext, ContextPackage, HybridRetrievalPackage

logger = logging.getLogger(__name__)

class TokenCounter(ABC):
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass

class HeuristicTokenCounter(TokenCounter):
    """
    Simple heuristic tokenizer (approx. 4 characters per token).
    Can be replaced later by a provider-specific tokenizer (e.g. tiktoken or Bedrock specific).
    """
    def count_tokens(self, text: str) -> int:
        if not text:
            return 0
        return len(text) // 4 + 1

class ContextBuilder:
    """
    Assembles the final ContextPackage for the AI Orchestrator.
    Handles deduplication, citation generation, token budget enforcement, and provenance tracking.
    """
    def __init__(self, token_counter: TokenCounter = HeuristicTokenCounter()):
        self.token_counter = token_counter

    def build_context(self, package: HybridRetrievalPackage, max_tokens: int = 8000) -> ContextPackage:
        """
        Builds the context respecting max_tokens. 
        Higher ranked chunks are prioritized.
        """
        retrieved_chunks = []
        citations: List[Dict[str, Any]] = []
        provenances: List[Dict[str, Any]] = []
        
        seen_docs: Set[int] = set()
        seen_chunks: Set[str] = set()
        
        current_tokens = 0
        
        for chunk in package.chunks:
            if chunk.chunk_id in seen_chunks:
                continue
                
            chunk_tokens = self.token_counter.count_tokens(chunk.text)
            
            # If adding this chunk exceeds the budget, we stop adding more chunks.
            if current_tokens + chunk_tokens > max_tokens:
                logger.info(f"Context budget reached ({current_tokens} tokens). Truncating remaining chunks.")
                break
                
            # Add chunk
            retrieved_chunks.append(chunk)
            seen_chunks.add(chunk.chunk_id)
            current_tokens += chunk_tokens
            
            # Process citations and provenance
            # Citation matches specific chunk metadata
            citation = {
                "chunk_id": chunk.chunk_id,
                "document_name": chunk.document_name,
                "section": chunk.section,
                "page": chunk.page_numbers[0] if chunk.page_numbers else None
            }
            citations.append(citation)
            
            # Document-level provenance (deduplicated)
            if chunk.document_id not in seen_docs:
                seen_docs.add(chunk.document_id)
                provenance = {
                    "document_id": chunk.document_id,
                    "document_name": chunk.document_name,
                    # Fallbacks if detailed provenance isn't passed yet.
                    "source_type": "Internal Document",
                    "trust_score": chunk.score
                }
                provenances.append(provenance)

        confidence = 0.0
        if retrieved_chunks:
            # Average score of included chunks
            confidence = sum(c.score for c in retrieved_chunks) / len(retrieved_chunks)

        return ContextPackage(
            query=package.query,
            retrieved_chunks=retrieved_chunks,
            citations=citations,
            provenance=provenances,
            confidence=round(confidence, 4),
            token_count=current_tokens
        )

# Export singleton instance
context_builder = ContextBuilder()
