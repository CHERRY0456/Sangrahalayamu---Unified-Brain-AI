import hashlib
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class EmbeddingMetadata(BaseModel):
    chunk_id: str
    provider: str
    model: str
    dimensions: int
    checksum: str
    success: bool

class EmbeddingInterface(ABC):
    @abstractmethod
    def generate_embedding_vectors(self, texts: List[str]) -> List[List[float]]:
        """
        Generates high-dimensional embedding vectors in memory (used only during validation).
        """
        pass

    @abstractmethod
    def generate_embedding_payload(self, chunk_id: str, text: str) -> EmbeddingMetadata:
        """
        Extracts structural embedding metadata to save in database chunks.
        """
        pass

class MockEmbeddingProvider(EmbeddingInterface):
    """
    Mock implementation of EmbeddingInterface generating 1536-dimensional vectors deterministic on text hashing.
    """
    def __init__(self, provider: str = "MockAWSBedrock", model: str = "amazon.titan-embed-text-v1", dimensions: int = 1536):
        self.provider = provider
        self.model = model
        self.dimensions = dimensions

    def generate_embedding_vectors(self, texts: List[str]) -> List[List[float]]:
        vectors = []
        for text in texts:
            # Hash text to seed floats
            hasher = hashlib.sha256(text.encode("utf-8"))
            seed = hasher.digest()
            vector = []
            for i in range(self.dimensions):
                val = float((seed[i % 32] + i * 17) % 256) / 256.0
                vector.append(round(val, 6))
            vectors.append(vector)
        return vectors

    def generate_embedding_payload(self, chunk_id: str, text: str) -> EmbeddingMetadata:
        checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return EmbeddingMetadata(
            chunk_id=chunk_id,
            provider=self.provider,
            model=self.model,
            dimensions=self.dimensions,
            checksum=checksum,
            success=True
        )

from sqlalchemy.orm import Session
from .stage import PipelineStage, PipelineContext

class EmbeddingsStage(PipelineStage):
    """
    Pipeline stage wrapper for generating embedding payload metadata.
    """
    def __init__(self, provider: Optional[EmbeddingInterface] = None):
        self.provider = provider or MockEmbeddingProvider()

    def execute(self, context: PipelineContext, db: Session) -> None:
        if context.chunks is None:
            raise ValueError("Chunking stage must run before Embeddings stage.")
            
        for chunk in context.chunks:
            # Generate 1536-dimensional mock vectors in memory for validation (per user request)
            _mock_vectors = self.provider.generate_embedding_vectors([chunk.text])
            
            # Persist only structural embedding metadata inside chunk payload
            payload_metadata = self.provider.generate_embedding_payload(
                chunk_id=chunk.chunk_id,
                text=chunk.text
            )
            chunk.embedding_metadata = payload_metadata.model_dump()

