from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class LLMRequest(BaseModel):
    """
    Standardized, provider-agnostic request parameters passed to LLMProviders.
    """
    prompt: str
    system_prompt: str
    max_tokens: int = 1024
    temperature: float = 0.0
    history: List[Dict[str, str]] = Field(default_factory=list)

class LLMResponse(BaseModel):
    """
    Standardized response returned by all LLMProviders (Ticket #8 constraint).
    """
    text: str
    token_usage: Dict[str, int] = Field(default_factory=dict)
    provider_name: str
    raw_response: Optional[Dict[str, Any]] = None

class Citation(BaseModel):
    """
    Structured citation reference mapping facts back to verified chunk sources.
    """
    document_name: str
    section: str
    page: int
    chunk_id: str
    matched_text: str

class ValidationResult(BaseModel):
    """
    Structured validation results checking grounding and hallucinations (Ticket #8 constraint).
    """
    is_valid: bool
    confidence: float  # Score from 0.0 to 1.0
    failed_checks: List[str] = Field(default_factory=list)
    retry_recommended: bool = False
    warnings: List[str] = Field(default_factory=list)

class GenerationMetadata(BaseModel):
    """
    Metadata summarizing prompt templates, model executions, and validation attempts (Ticket #8 constraint).
    """
    provider: str
    model: str
    prompt_template: str
    retrieval_context_size: int
    validation_attempts: int
    orchestrator_version: str = "1.0.0"

class AIResponse(BaseModel):
    """
    Standardized response returned by the AI Orchestrator to conversational clients.
    """
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    confidence: float
    retrieval_summary: Dict[str, Any] = Field(default_factory=dict)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    token_usage: Dict[str, int] = Field(default_factory=dict)
    latency: Dict[str, float] = Field(default_factory=dict)  # request metrics
    generation_metadata: Optional[GenerationMetadata] = None
    transparency_report: Optional[Any] = None
