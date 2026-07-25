"""
Multi-Database Indexer for Industrial Ingestion.
Indexes extracted entities, vectors, and graph relationships into PostgreSQL, Qdrant, Neo4j, and AWS Bedrock.
"""
import uuid
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.qdrant.qdrant_service import qdrant_service
from app.services.graph.providers.neo4j_provider import get_neo4j_provider
from app.services.embeddings.embedding_service import embedding_service
from app.services.embeddings.schemas.embedding_models import EmbeddingVector
from .parsers.base import ParsedDocument

logger = logging.getLogger("industrybrain.processing.indexer")


class IndustrialIndexer:
    def index(self, db: Session, parsed_doc: ParsedDocument, user_id: str, workspace_id: str = "default") -> Dict[str, Any]:
        """
        Indexes parsed document across PostgreSQL, Qdrant Vector DB, and Neo4j Graph DB.
        """
        doc_id = str(uuid.uuid4())
        logger.info(f"[IndustrialIndexer] Indexing document '{parsed_doc.filename}' (ID: {doc_id}) across all databases")

        # 1. PostgreSQL RDBMS Persistence
        doc_record = Document(
            id=doc_id,
            filename=parsed_doc.filename,
            file_type=parsed_doc.file_type,
            classification=parsed_doc.metadata.get("classification", "Internal"),
            status="COMPLETED",
            user_id=user_id,
            workspace_id=workspace_id
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)
        logger.info(f"[PostgreSQL] Successfully saved Document record '{doc_id}'")

        # 2. AWS Bedrock Embeddings + Qdrant Vector DB Ingestion
        chunk_dicts = []
        embedding_vectors: List[EmbeddingVector] = []
        
        for c in parsed_doc.chunks:
            # Generate vector embedding for chunk text using Bedrock / Titan
            emb_vec = embedding_service.embed_text(c.content)
            embedding_vectors.append(emb_vec)
            
            chunk_dicts.append({
                "chunk_id": str(uuid.uuid4()),
                "text": c.content,
                "metadata": {
                    "source": parsed_doc.filename,
                    "page": c.page_number,
                    "heading": c.section_heading or "General"
                },
                "entities": parsed_doc.equipment_tags,
                "relationships": []
            })

        if chunk_dicts:
            try:
                qdrant_service.upsert_document_chunks(
                    document_id=doc_id,
                    workspace_id=workspace_id,
                    role_permissions=["all"],
                    chunks=chunk_dicts,
                    embeddings=embedding_vectors
                )
                logger.info(f"[Qdrant] Successfully upserted {len(chunk_dicts)} chunks for doc '{doc_id}'")
            except Exception as e:
                logger.warning(f"[Qdrant] Vector upsert warning: {e}")

        # 3. Neo4j Graph Database Topology Ingestion
        try:
            neo4j_provider = get_neo4j_provider()
            with neo4j_provider.session() as session:
                # Create Document Node
                session.run(
                    """
                    MERGE (d:Document {id: $doc_id})
                    SET d.filename = $filename, d.file_type = $file_type, d.workspace_id = $workspace_id
                    """,
                    doc_id=doc_id,
                    filename=parsed_doc.filename,
                    file_type=parsed_doc.file_type,
                    workspace_id=workspace_id
                )

                # Create Equipment Tags and link to Document
                for tag in parsed_doc.equipment_tags:
                    session.run(
                        """
                        MERGE (e:Equipment {tag: $tag})
                        SET e.workspace_id = $workspace_id
                        WITH e
                        MATCH (d:Document {id: $doc_id})
                        MERGE (d)-[:GOVERNS]->(e)
                        """,
                        tag=tag,
                        doc_id=doc_id,
                        workspace_id=workspace_id
                    )
            logger.info(f"[Neo4j] Graph topology created: {len(parsed_doc.equipment_tags)} equipment nodes linked")
        except Exception as e:
            logger.warning(f"[Neo4j] Graph topology warning: {e}")

        return {
            "document_id": doc_id,
            "filename": parsed_doc.filename,
            "chunks_indexed": len(chunk_dicts),
            "equipment_tags_discovered": len(parsed_doc.equipment_tags),
            "tables_extracted": len(parsed_doc.tables),
            "status": "COMPLETED"
        }


industrial_indexer = IndustrialIndexer()
