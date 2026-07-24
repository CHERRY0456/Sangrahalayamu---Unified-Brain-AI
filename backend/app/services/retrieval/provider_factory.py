from .semantic import VectorRetrievalProvider, QdrantVectorRetrievalProvider
from .graph import GraphRetrievalProvider, Neo4jGraphRetrievalProvider

class RetrievalProviderFactory:
    """
    Factory resolving active semantic vector and graph database search engines.
    """
    @staticmethod
    def get_vector_provider() -> VectorRetrievalProvider:
        # Use true Qdrant provider
        return QdrantVectorRetrievalProvider()

    @staticmethod
    def get_graph_provider() -> GraphRetrievalProvider:
        # Switch to Neo4j for Phase 4
        return Neo4jGraphRetrievalProvider()
