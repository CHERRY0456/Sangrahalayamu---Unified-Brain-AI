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
            # Fallback to a mock provider if configured, or raise
            if provider_enum == EmbeddingProviderEnum.MOCK:
                return self._mock_provider()
            logger.warning(f"Embedding provider {provider_enum} not implemented. Falling back to Bedrock.")
            return BedrockEmbeddingProvider()

    def _mock_provider(self) -> BaseEmbeddingProvider:
        class MockProvider(BaseEmbeddingProvider):
            def embed_text(self, text: str) -> EmbeddingVector:
                return self.embed_batch([text])[0]
            
            def embed_batch(self, texts: List[str]) -> List[EmbeddingVector]:
                import random
                dim = settings.embedding.dimension
                return [
                    EmbeddingVector(
                        vector=[random.random() for _ in range(dim)],
                        model="mock-model",
                        provider=EmbeddingProviderEnum.MOCK,
                        dimensions=dim,
                        usage={"input_tokens": len(t.split())}
                    ) for t in texts
                ]
        return MockProvider()

    def embed_text(self, text: str) -> EmbeddingVector:
        return self.provider.embed_text(text)

    def embed_batch(self, texts: List[str]) -> List[EmbeddingVector]:
        # Handle chunking of batches if necessary, depending on the provider limits.
        # For simplicity, passing directly to the provider for now.
        return self.provider.embed_batch(texts)

embedding_service = EmbeddingService()
