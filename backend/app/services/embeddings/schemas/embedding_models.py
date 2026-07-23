from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from app.core.enums import EmbeddingProviderEnum

class EmbeddingVector(BaseModel):
    """
    Standardized payload for an embedding vector across the platform.
    """
    vector: List[float] = Field(..., description="The dense vector embedding")
    model: str = Field(..., description="The ID of the model used to generate the embedding")
    provider: EmbeddingProviderEnum = Field(..., description="The provider of the embedding (e.g. BEDROCK)")
    dimensions: int = Field(..., description="The dimensionality of the vector")
    latency: float = Field(0.0, description="Latency in seconds to generate the embedding")
    usage: Dict[str, int] = Field(default_factory=dict, description="Token usage (e.g. {'prompt_tokens': 15})")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context or diagnostics")
