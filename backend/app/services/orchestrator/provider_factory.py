from app.core.config import settings
from .providers import LLMProvider, BedrockProvider

class LLMProviderFactory:
    """
    Factory resolving configured active LLMProvider instances.
    """
    @staticmethod
    def get_llm_provider() -> LLMProvider:
        provider_name = settings.llm.provider.lower().strip()
        
        if provider_name == "bedrock":
            return BedrockProvider()
        else:
            # Enforce Zero-Mock Production Mandate
            return BedrockProvider()
