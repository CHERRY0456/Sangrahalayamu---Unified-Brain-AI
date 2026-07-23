import logging
import json
from typing import List, Dict, Any, Optional
from neo4j import AsyncGraphDatabase, AsyncSession

from app.core.config import settings
from ..interfaces.graph_provider import BaseGraphProvider
from ..schemas.graph_models import GraphNode, GraphRelationship, GraphPath

logger = logging.getLogger(__name__)

class Neo4jProvider(BaseGraphProvider):
    """
    Neo4j Async implementation for Graph Operations.
    """
    def __init__(self):
        self.uri = settings.neo4j.uri
        self.username = settings.neo4j.username
        self.password = settings.neo4j.password
        self.database = settings.neo4j.database
        self.driver = None

    async def connect(self):
        if not self.driver:
            self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.username, self.password))
            logger.info("Connected to Neo4j.")

    async def close(self):
        if self.driver:
            await self.driver.close()
            self.driver = None
            logger.info("Closed Neo4j connection.")

    async def _get_session(self) -> AsyncSession:
        if not self.driver:
            await self.connect()
        return self.driver.session(database=self.database)

    async def upsert_node(self, node: GraphNode):
        await self.upsert_nodes_batch([node])

    async def upsert_nodes_batch(self, nodes: List[GraphNode]):
        if not nodes:
            return
        
        # Build batch parameters
        batch = []
        for n in nodes:
            batch.append({
                "id": n.id,
                "labels": [lbl.value for lbl in n.labels],
                "properties": n.properties
            })

        query = """
        UNWIND $batch AS row
        CALL apoc.merge.node(row.labels, {id: row.id}, row.properties, row.properties)
        YIELD node
        RETURN count(node)
        """
        # Note: apoc.merge.node requires APOC. A pure Cypher alternative for dynamic labels is trickier 
        # but since labels are known, we might need a dynamic query if APOC is not available.
        # Assuming APOC is available as standard for enterprise neo4j.
        
        async with await self._get_session() as session:
            try:
                await session.run(query, batch=batch)
            except Exception as e:
                logger.error(f"Failed batch node upsert: {e}")
                # Fallback to pure cypher if APOC fails (one label at a time)
                for n in nodes:
                    lbls = ":".join([lbl.value for lbl in n.labels])
                    fallback_q = f"MERGE (n:{lbls} {{id: $id}}) SET n += $props"
                    await session.run(fallback_q, id=n.id, props=n.properties)

    async def upsert_relationship(self, relationship: GraphRelationship):
        await self.upsert_relationships_batch([relationship])

    async def upsert_relationships_batch(self, relationships: List[GraphRelationship]):
        if not relationships:
            return
            
        # Group by relationship type because MERGE requires static relationship types in pure Cypher
        grouped = {}
        for r in relationships:
            rel_type = r.type.value
            if rel_type not in grouped:
                grouped[rel_type] = []
            
            grouped[rel_type].append({
                "source_id": r.source_id,
                "target_id": r.target_id,
                "confidence": r.confidence,
                "properties": r.properties,
                "provenance": json.dumps(r.provenance) if r.provenance else "{}"
            })
            
        async with await self._get_session() as session:
            for rel_type, batch in grouped.items():
                query = f"""
                UNWIND $batch AS row
                MATCH (s {{id: row.source_id}})
                MATCH (t {{id: row.target_id}})
                MERGE (s)-[r:{rel_type}]->(t)
                SET r += row.properties
                SET r.confidence = row.confidence
                SET r.provenance = row.provenance
                """
                try:
                    await session.run(query, batch=batch)
                except Exception as e:
                    logger.error(f"Failed batch relationship upsert for type {rel_type}: {e}")

    async def get_shortest_path(self, source_id: str, target_id: str, max_depth: int = 5) -> Optional[GraphPath]:
        query = f"""
        MATCH p = shortestPath((s {{id: $source_id}})-[*..{max_depth}]-(t {{id: $target_id}}))
        RETURN nodes(p) AS path_nodes, relationships(p) AS path_rels
        """
        async with await self._get_session() as session:
            result = await session.run(query, source_id=source_id, target_id=target_id)
            record = await result.single()
            if not record:
                return None
                
            nodes = []
            # In neo4j python driver, record["path_nodes"] is a list of neo4j.graph.Node
            for n in record["path_nodes"]:
                nodes.append(GraphNode(
                    id=n.get("id"),
                    labels=list(n.labels),
                    properties=dict(n)
                ))
                
            rels = []
            for r in record["path_rels"]:
                rels.append(GraphRelationship(
                    source_id=r.start_node.get("id"),
                    target_id=r.end_node.get("id"),
                    type=r.type,
                    properties=dict(r),
                    confidence=r.get("confidence", 1.0)
                ))
                
            return GraphPath(nodes=nodes, relationships=rels)

    async def get_neighborhood(self, node_id: str, depth: int = 1) -> List[GraphRelationship]:
        query = f"""
        MATCH (s {{id: $node_id}})-[r*1..{depth}]-(t)
        RETURN last(r) AS rel, startNode(last(r)) AS src, endNode(last(r)) AS tgt
        """
        rels = []
        async with await self._get_session() as session:
            result = await session.run(query, node_id=node_id)
            async for record in result:
                rel = record["rel"]
                src = record["src"]
                tgt = record["tgt"]
                rels.append(GraphRelationship(
                    source_id=src.get("id"),
                    target_id=tgt.get("id"),
                    type=rel.type,
                    properties=dict(rel),
                    confidence=rel.get("confidence", 1.0)
                ))
        return rels

    async def extract_subgraph(self, query_params: Dict[str, Any]) -> List[GraphPath]:
        # Implementation depends on specific agent needs (e.g., finding a compliance chain)
        return []

    async def health_check(self) -> bool:
        try:
            async with await self._get_session() as session:
                result = await session.run("RETURN 1")
                await result.single()
                return True
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False
