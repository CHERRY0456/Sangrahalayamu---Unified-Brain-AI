import logging
from typing import AsyncGenerator

from app.core.config import settings
from .interfaces.llm_provider import BaseLLMProvider
from .providers.bedrock_qwen_provider import BedrockQwenProvider
from .schemas.generation_models import GenerationRequest, GenerationResponse, StreamEvent

logger = logging.getLogger(__name__)

class LLMService:
    """
    Centralized service for interacting with LLMs.
    Provider-agnostic interface that resolves the correct provider instance.
    """
    def __init__(self):
        self.provider = self._resolve_provider()

    def _resolve_provider(self) -> BaseLLMProvider:
        # Based on settings, return BedrockQwenProvider
        # Extensible to OpenAI, Anthropic, etc.
        return BedrockQwenProvider()

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        logger.info(f"Generating LLM response (sync) | max_tokens={request.max_tokens} | temp={request.temperature}")
        return self.provider.generate(request)

    async def stream_generate(self, request: GenerationRequest) -> AsyncGenerator[StreamEvent, None]:
        logger.info(f"Generating LLM response (stream) | max_tokens={request.max_tokens} | temp={request.temperature}")
        async for event in self.provider.stream_generate(request):
            yield event

    def health_check(self) -> bool:
        return self.provider.health_check()

llm_service = LLMService()
