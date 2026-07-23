from typing import List, Any
from .graph import GraphRecommendationProvider
from .metadata import MetadataRecommendationProvider
from .semantic import SemanticRecommendationProvider

class RecommendationProviderFactory:
    """
    Factory resolving active recommendation strategy provider instances.
    """
    @staticmethod
    def get_providers() -> List[Any]:
        return [
            GraphRecommendationProvider(),
            MetadataRecommendationProvider(),
            SemanticRecommendationProvider()
        ]
