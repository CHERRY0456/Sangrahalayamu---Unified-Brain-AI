import re
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.services.processing.models import (
    SemanticChunkPayload,
    ExtractedEntity,
    ExtractedRelationship,
    EmbeddingDocument,
    ProvenanceRecord,
    IngestionReport
)

logger = logging.getLogger("sangrahalayamu.processing.payload_prep")


class IngestionPayloadPreparer:
    """
    Assembles extracted structures (chunks, entities, relationships, layout nodes)
    into standard downstream EmbeddingDocument payloads and generates IngestionReports.
    """

    @staticmethod
    def prepare_embedding_documents(
        chunks: List[SemanticChunkPayload],
        entities: List[ExtractedEntity],
        relationships: List[ExtractedRelationship],
        doc_id: int,
        parser_name: str
    ) -> List[EmbeddingDocument]:
        """
        Maps entities and relationships to their corresponding semantic text chunk,
        creating structured EmbeddingDocuments for vector and graph indexing.
        """
        embedding_docs = []

        for chunk in chunks:
            chunk_text = chunk.text
            chunk_text_lower = chunk_text.lower()

            # Find entities mentioned in this chunk's text
            chunk_entities = []
            entity_names_in_chunk = set()
            for ent in entities:
                raw_pattern = ent.name.replace("-", "[- ]?")
                if re.search(r"\b" + raw_pattern + r"\b", chunk_text, re.IGNORECASE):
                    chunk_entities.append(ent)
                    entity_names_in_chunk.add(ent.name)

            # Find relationships where BOTH source and target are mentioned in this chunk
            chunk_relationships = []
            for rel in relationships:
                if rel.source in entity_names_in_chunk and rel.target in entity_names_in_chunk:
                    chunk_relationships.append(rel)

            # Derive page from chunk page numbers
            page_no = chunk.page_numbers[0] if chunk.page_numbers else 1

            prov = ProvenanceRecord(
                document_id=doc_id,
                page=page_no,
                section=chunk.section,
                parser=parser_name,
                extraction_method="semantic_proximity_mapping",
                confidence=1.0,
                timestamp=datetime.utcnow()
            )

            # Extra metadata properties for index mappings
            metadata = {
                "section": chunk.section,
                "heading_hierarchy": chunk.heading_hierarchy,
                "page_numbers": chunk.page_numbers,
                "parent_doc_id": chunk.parent_doc_id,
                "token_count": chunk.token_count
            }

            embedding_docs.append(EmbeddingDocument(
                chunk_id=chunk.chunk_id,
                text=chunk_text,
                metadata=metadata,
                entities=chunk_entities,
                relationships=chunk_relationships,
                provenance=prov
            ))

        return embedding_docs

    @staticmethod
    def generate_report(
        parser_name: str,
        modality: str,
        latency_ms: float,
        character_count: int,
        chunk_count: int,
        entity_count: int,
        relationship_count: int,
        confidence_scores: List[float],
        warnings: List[str]
    ) -> IngestionReport:
        """
        Creates a structured IngestionReport for UI and operational monitoring.
        """
        avg_conf = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 1.0
        
        return IngestionReport(
            parser_name=parser_name,
            modality_detected=modality,
            parse_latency_ms=round(latency_ms, 2),
            character_count=character_count,
            chunk_count=chunk_count,
            entity_count=entity_count,
            relationship_count=relationship_count,
            average_confidence=round(avg_conf, 2),
            warnings=warnings,
            timestamp=datetime.utcnow()
        )
