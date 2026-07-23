import logging
from typing import List, Optional
from app.services.graph.graph_repository import graph_repository
from app.services.graph.schemas.graph_models import GraphRelationship

logger = logging.getLogger(__name__)

class GraphRetrievalEngine:
    """
    Handles graph-based retrieval logic (neighborhood queries, related assets, etc.).
    """
    
    async def get_related_assets(self, asset_id: str, depth: int = 2) -> List[GraphRelationship]:
        """Retrieve all relationships spanning out from an asset."""
        return await graph_repository.get_neighborhood(node_id=asset_id, depth=depth)
        
    async def get_similar_failures(self, failure_mode_id: str, depth: int = 2) -> List[GraphRelationship]:
        """Retrieve failure modes and connected incidents."""
        return await graph_repository.get_neighborhood(node_id=failure_mode_id, depth=depth)

    async def get_connected_procedures(self, entity_id: str, depth: int = 1) -> List[GraphRelationship]:
        """Retrieve procedures and tasks connected to an entity."""
        return await graph_repository.get_neighborhood(node_id=entity_id, depth=depth)
        
    async def get_maintenance_history(self, equipment_id: str) -> List[GraphRelationship]:
        """Specific pull for maintenance tasks connected to equipment."""
        return await graph_repository.get_neighborhood(node_id=equipment_id, depth=1)

graph_retrieval_engine = GraphRetrievalEngine()
