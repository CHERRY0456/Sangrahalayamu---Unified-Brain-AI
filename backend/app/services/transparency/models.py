from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ConfidenceAnalysis(BaseModel):
    confidence: float
    reason: str
    provenance: str = Field(default="validator", description="Source of the verification analysis")

class RetrievalSummary(BaseModel):
    num_documents_considered: int
    metadata_filters_applied: Dict[str, Any]
    num_semantic_matches: int
    num_graph_relations_expanded: int
    fusion_weights: Dict[str, float]
    description: str
    provenance: str = Field(default="retrieval_engine", description="Source of retrieval analysis")

class PermissionSummary(BaseModel):
    user_role: str
    clearance_level: str
    temporary_override_status: bool
    sections_excluded: List[str] = Field(default_factory=list)
    documents_excluded: List[str] = Field(default_factory=list)
    reason: str
    provenance: str = Field(default="policy_engine", description="Source of safety evaluation details")

class CitationSummary(BaseModel):
    citation_count: int
    duplicate_citations_count: int
    unused_retrieved_chunks: List[str] = Field(default_factory=list)  # chunk IDs
    missing_citations: bool
    provenance: str = Field(default="citation_auditor", description="Source of citation validation")

class ExecutionTrace(BaseModel):
    latencies: Dict[str, float]
    provider: str
    model: str
    prompt_template: str
    provenance: str = Field(default="orchestrator_tracker", description="Source of runtime profiles")

class TransparencyReport(BaseModel):
    """
    Standardized, explainable transparency report with section-level provenance fields (Ticket #9 constraint).
    """
    confidence_analysis: ConfidenceAnalysis
    retrieval: RetrievalSummary
    permissions: PermissionSummary
    citations: CitationSummary
    warnings: List[str] = Field(default_factory=list)
    execution_trace: Optional[ExecutionTrace] = None
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    diagnostics: Optional[Dict[str, Any]] = None
    provenance: str = Field(default="transparency_engine", description="Root transparency generator")
