from typing import List
import logging

from app.core.config import settings
from app.core.enums import EmbeddingProviderEnum
from .interfaces.embedding_provider import BaseEmbeddingProvider
from .schemas.embedding_models import EmbeddingVector
from .providers.bedrock_embedding_provider import BedrockEmbeddingProvider

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Centralized service for generating embeddings across the platform.
    Provider-agnostic interface that resolves the correct provider instance.
    """
    def __init__(self):
        self.provider = self._resolve_provider()

    def _resolve_provider(self) -> BaseEmbeddingProvider:
        provider_enum = settings.embedding.provider
        
        if provider_enum == EmbeddingProviderEnum.BEDROCK:
            return BedrockEmbeddingProvider()
        else:
            logger.warning(f"Embedding provider {provider_enum} not fully implemented. Falling back to Bedrock.")
            return BedrockEmbeddingProvider()

    def embed_text(self, text: str) -> EmbeddingVector:
        return self.provider.embed_text(text)

    def embed_batch(self, texts: List[str]) -> List[EmbeddingVector]:
        # Handle chunking of batches if necessary, depending on the provider limits.
        # For simplicity, passing directly to the provider for now.
        return self.provider.embed_batch(texts)

embedding_service = EmbeddingService()
