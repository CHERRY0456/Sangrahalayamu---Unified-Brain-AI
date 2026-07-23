from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class GenerationRequest(BaseModel):
    """
    Standardized payload for requesting generation from an LLM.
    """
    prompt: str = Field(..., description="The fully constructed prompt")
    system_prompt: Optional[str] = Field(None, description="Optional system-level instructions")
    temperature: float = Field(0.0, description="Sampling temperature")
    max_tokens: int = Field(2048, description="Maximum tokens to generate")
    stop_sequences: List[str] = Field(default_factory=list, description="Sequences that stop generation")
    
class GenerationResponse(BaseModel):
    """
    Standardized return type for LLM generation.
    """
    text: str = Field(..., description="The raw generated text")
    model_id: str = Field(..., description="The model ID used")
    provider: str = Field(..., description="The provider name (e.g. Bedrock)")
    usage: Dict[str, int] = Field(default_factory=dict, description="Token usage details")
    latency: float = Field(0.0, description="Latency in seconds")
    finish_reason: Optional[str] = Field(None, description="Reason for stopping")

class StreamEvent(BaseModel):
    """
    Delta chunks returned during streaming generation.
    """
    chunk: str = Field(..., description="The delta text content")
    is_final: bool = Field(False, description="True if this is the final event")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Final metadata (usage, metrics) populated only when is_final=True")
