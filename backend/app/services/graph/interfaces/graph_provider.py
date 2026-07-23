from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..schemas.graph_models import GraphNode, GraphRelationship, GraphPath

class BaseGraphProvider(ABC):
    """
    Abstract interface for Graph Database operations.
    """
    
    @abstractmethod
    async def connect(self):
        """Initialize the connection to the graph database."""
        pass
        
    @abstractmethod
    async def close(self):
        """Close the connection."""
        pass

    @abstractmethod
    async def upsert_node(self, node: GraphNode):
        pass

    @abstractmethod
    async def upsert_nodes_batch(self, nodes: List[GraphNode]):
        pass

    @abstractmethod
    async def upsert_relationship(self, relationship: GraphRelationship):
        pass

    @abstractmethod
    async def upsert_relationships_batch(self, relationships: List[GraphRelationship]):
        pass
        
    @abstractmethod
    async def get_shortest_path(self, source_id: str, target_id: str, max_depth: int = 5) -> Optional[GraphPath]:
        pass

    @abstractmethod
    async def get_neighborhood(self, node_id: str, depth: int = 1) -> List[GraphRelationship]:
        pass
        
    @abstractmethod
    async def extract_subgraph(self, query_params: Dict[str, Any]) -> List[GraphPath]:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass
