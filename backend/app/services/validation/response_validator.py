import json
import re
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class CitationSchema(BaseModel):
    chunk_id: str
    relevance: str

class AIResponse(BaseModel):
    """
    Standardized, safe, and final response object emitted by the AI Orchestrator.
    No endpoint should return raw LLM text.
    """
    answer: str
    summary: str
    citations: List[CitationSchema]
    confidence: float
    recommended_actions: List[str]
    warnings: List[str]
    metadata: Optional[Dict[str, Any]] = None
    provenance: Optional[List[Dict[str, Any]]] = None

class ResponseValidator:
    """
    Validates that the raw LLM response meets enterprise constraints.
    """
    def validate_and_parse(self, raw_text: str) -> AIResponse:
        # Strip potential markdown code blocks (e.g., ```json ... ```)
        clean_text = raw_text.strip()
        if clean_text.startswith("```"):
            clean_text = re.sub(r"^```(?:json)?", "", clean_text)
            clean_text = re.sub(r"```$", "", clean_text).strip()
            
        try:
            parsed_json = json.loads(clean_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON. Raw text: {raw_text[:200]}...")
            raise ValueError("LLM returned malformed JSON.")

        try:
            response_obj = AIResponse(**parsed_json)
        except ValidationError as e:
            logger.error(f"LLM response failed schema validation: {e}")
            raise ValueError("LLM response violated structural guardrails.")

        # Additional Guardrail Checks
        if not response_obj.answer.strip():
            raise ValueError("Empty response answer generated.")
            
        return response_obj

class ResponseFormatter:
    """
    Formats the validated response, attaching metadata and provenance from the context package.
    """
    def format_response(self, validated_response: AIResponse, metadata: dict, provenance: list) -> AIResponse:
        validated_response.metadata = metadata
        validated_response.provenance = provenance
        return validated_response

response_validator = ResponseValidator()
response_formatter = ResponseFormatter()
