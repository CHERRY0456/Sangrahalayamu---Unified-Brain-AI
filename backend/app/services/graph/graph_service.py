import logging
from app.services.processing.schemas.parser_models import ParserResult
from .graph_builder import graph_builder
from .graph_repository import graph_repository

logger = logging.getLogger(__name__)

class GraphService:
    """
    Coordinates building and inserting graphs into the repository.
    """
    async def ingest_parser_result(self, result: ParserResult):
        """
        Takes a processed ParserResult from Phase 1, builds nodes/relationships, 
        and batch upserts them into Neo4j.
        """
        logger.info(f"Ingesting graph data for document {result.document_id}")
        nodes, relationships = graph_builder.build_from_parser_result(result)
        
        # Batch insert nodes
        await graph_repository.upsert_nodes_batch(nodes)
        
        # Batch insert relationships
        await graph_repository.upsert_relationships_batch(relationships)
        
        logger.info(f"Successfully ingested {len(nodes)} nodes and {len(relationships)} relationships.")

graph_service = GraphService()
