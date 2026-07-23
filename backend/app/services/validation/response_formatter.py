import logging
from typing import Dict, Any, List
from .response_validator import AIResponse

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """
    Formats the validated response, attaching metadata and provenance from the context package.
    """
    def format_response(self, validated_response: AIResponse, metadata: dict, provenance: list) -> AIResponse:
        validated_response.metadata = metadata
        validated_response.provenance = provenance
        return validated_response

response_formatter = ResponseFormatter()
