from abc import ABC, abstractmethod
from typing import AsyncGenerator
from ..schemas.generation_models import GenerationRequest, GenerationResponse, StreamEvent

class BaseLLMProvider(ABC):
    """
    Abstract interface for LLM providers.
    """
    
    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """
        Generates a standard synchronous response.
        """
        pass
        
    @abstractmethod
    async def stream_generate(self, request: GenerationRequest) -> AsyncGenerator[StreamEvent, None]:
        """
        Generates a streaming asynchronous response.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Checks if the provider is reachable and healthy.
        """
        pass
