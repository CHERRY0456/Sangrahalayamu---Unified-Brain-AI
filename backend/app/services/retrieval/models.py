from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class RetrievalFilters(BaseModel):
    """
    Metadata query filter constraints matching user criteria.
    """
    department: Optional[str] = None
    doc_type: Optional[str] = None
    plant: Optional[str] = None
    equipment: Optional[List[str]] = None
    author: Optional[str] = None
    classification: Optional[str] = None
    version: Optional[str] = None

class RetrievalMatch(BaseModel):
    """
    A single chunk match record returned by a specific backend provider.
    """
    chunk_id: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RetrievalProviderResult(BaseModel):
    """
    Standardized wrapper returned by both Semantic and Graph providers (Ticket #7 constraint).
    """
    matches: List[RetrievalMatch]
    provider_name: str
    diagnostics: Dict[str, Any] = Field(default_factory=dict)

class RetrievedChunkContext(BaseModel):
    """
    Enriched context record returned as part of the unified AI package.
    """
    chunk_id: str
    document_id: int
    document_name: str
    section: str
    text: str
    page_numbers: List[int]
    score: float  # Normalized, fused final score
    rank_explanation: str

class GraphContext(BaseModel):
    """
    Structural graph connection paths ready for contextual explanation.
    """
    source: str
    target: str
    relationship_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class HybridRetrievalPackage(BaseModel):
    """
    Final, permission-aware response context packaging all details for AI generation.
    """
    query: str
    chunks: List[RetrievedChunkContext]
    graph_relationships: List[GraphContext]
    metadata_summary: Dict[str, Any] = Field(default_factory=dict)
    explanation: str
    diagnostics: Optional[Dict[str, Any]] = None

class ContextPackage(BaseModel):
    """
    The final packaged context sent to the LLM orchestrator.
    It includes deduplicated citations, strict token budget enforcement, and provenance.
    """
    query: str
    retrieved_chunks: List[RetrievedChunkContext]
    citations: List[Dict[str, Any]]
    provenance: List[Dict[str, Any]]
    confidence: float
    token_count: int
