import logging
from typing import List, Dict, Any, Optional

from .interfaces.graph_provider import BaseGraphProvider
from .providers.neo4j_provider import Neo4jProvider
from .schemas.graph_models import GraphNode, GraphRelationship, GraphPath

logger = logging.getLogger(__name__)

class GraphRepository:
    """
    Enterprise Graph Repository.
    Wraps the graph database provider to ensure zero Cypher/provider leakage.
    """
    def __init__(self, provider: BaseGraphProvider = None):
        self.provider = provider or Neo4jProvider()

    async def connect(self):
        await self.provider.connect()

    async def close(self):
        await self.provider.close()

    async def upsert_node(self, node: GraphNode):
        await self.provider.upsert_node(node)

    async def upsert_nodes_batch(self, nodes: List[GraphNode]):
        await self.provider.upsert_nodes_batch(nodes)

    async def upsert_relationship(self, relationship: GraphRelationship):
        await self.provider.upsert_relationship(relationship)

    async def upsert_relationships_batch(self, relationships: List[GraphRelationship]):
        await self.provider.upsert_relationships_batch(relationships)

    async def get_shortest_path(self, source_id: str, target_id: str, max_depth: int = 5) -> Optional[GraphPath]:
        return await self.provider.get_shortest_path(source_id, target_id, max_depth)

    async def get_neighborhood(self, node_id: str, depth: int = 1) -> List[GraphRelationship]:
        return await self.provider.get_neighborhood(node_id, depth)

    async def extract_subgraph(self, query_params: Dict[str, Any]) -> List[GraphPath]:
        return await self.provider.extract_subgraph(query_params)

    async def health_check(self) -> bool:
        return await self.provider.health_check()

graph_repository = GraphRepository()
