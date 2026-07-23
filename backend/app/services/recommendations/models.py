from typing import List, Dict, Any
from pydantic import BaseModel, Field

class RecommendationCandidate(BaseModel):
    """
    Common intermediate model returned by every strategy (Ticket #10 constraint).
    """
    document_id: int
    category: str
    base_score: float
    strategy: str
    explanation: str
    source_artifacts: List[str] = Field(default_factory=list)
    confidence: float

class Recommendation(BaseModel):
    """
    Structured recommendation returned in the final ranked package.
    """
    title: str
    category: str
    confidence: float
    explanation: str
    recommendation_reason_code: str
    source_documents: List[str] = Field(default_factory=list)

class RecommendationPackage(BaseModel):
    """
    Standardized proactive recommendation package.
    """
    recommendations: List[Recommendation] = Field(default_factory=list)
    category_summary: Dict[str, int] = Field(default_factory=dict)
    ranking_details: Dict[str, Any] = Field(default_factory=dict)
    sources: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
