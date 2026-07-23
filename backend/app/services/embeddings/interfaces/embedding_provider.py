from abc import ABC, abstractmethod
from typing import List
from ..schemas.embedding_models import EmbeddingVector

class BaseEmbeddingProvider(ABC):
    """
    Abstract interface for all embedding providers.
    """
    
    @abstractmethod
    def embed_text(self, text: str) -> EmbeddingVector:
        """
        Embeds a single string of text.
        """
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[EmbeddingVector]:
        """
        Embeds a batch of texts.
        """
        pass
