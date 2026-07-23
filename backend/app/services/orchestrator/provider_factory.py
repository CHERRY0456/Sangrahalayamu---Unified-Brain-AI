from app.core.config import settings
from .providers import LLMProvider, MockBedrockProvider, BedrockProvider

class LLMProviderFactory:
    """
    Factory resolving configured active LLMProvider instances.
    """
    @staticmethod
    def get_llm_provider() -> LLMProvider:
        provider_name = settings.llm.provider.lower().strip()
        
        if provider_name == "mock_bedrock" or provider_name == "mock":
            return MockBedrockProvider()
        elif provider_name == "bedrock":
            return BedrockProvider()
        else:
            # Fallback mock for standard testing safety
            return MockBedrockProvider()
