import logging
from typing import List, Dict, Any

from app.services.processing.schemas.parser_models import ParserResult, Entity, Relationship
from .schemas.graph_models import GraphNode, GraphRelationship, NodeType, RelationshipType
from .graph_repository import graph_repository

logger = logging.getLogger(__name__)

class GraphBuilder:
    """
    Transforms Phase 1 ParserResults into normalized GraphNodes and GraphRelationships.
    """
    def build_from_parser_result(self, result: ParserResult) -> tuple[List[GraphNode], List[GraphRelationship]]:
        nodes = []
        relationships = []
        
        # 1. Create a Document Node for provenance
        doc_node = GraphNode(
            id=result.document_id,
            labels=[NodeType.Document],
            properties={
                "name": result.metadata.get("filename", "Unknown Document"),
                "status": "PROCESSED"
            }
        )
        nodes.append(doc_node)
        
        # 2. Extract Entities into Nodes
        for ent in result.entities:
            # Map parser entity type to Graph NodeType
            try:
                # Naive mapping: assume the parser returns types that match NodeType Enum
                # If not, fallback to 'Asset' or handle custom mapping
                node_type = NodeType(ent.type)
            except ValueError:
                node_type = NodeType.Asset
                
            n = GraphNode(
                id=ent.id,
                labels=[node_type],
                properties={
                    "name": ent.name,
                    "confidence": ent.confidence
                }
            )
            nodes.append(n)
            
            # Connect entity to Document for provenance
            r_prov = GraphRelationship(
                source_id=ent.id,
                target_id=doc_node.id,
                type=RelationshipType.DESCRIBES, # or a new type like EXTRACTED_FROM
                confidence=1.0,
                provenance={"source": "IngestionPipeline"}
            )
            relationships.append(r_prov)

        # 3. Extract Relationships
        for rel in result.relationships:
            try:
                rel_type = RelationshipType(rel.type.upper())
            except ValueError:
                rel_type = RelationshipType.RELATED_TO
                
            r = GraphRelationship(
                source_id=rel.source_id,
                target_id=rel.target_id,
                type=rel_type,
                confidence=rel.confidence,
                properties=rel.properties
            )
            relationships.append(r)
            
        return nodes, relationships

graph_builder = GraphBuilder()
