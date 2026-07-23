from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ParsedElement(BaseModel):
    type: str  # heading, paragraph, table, list
    text: str
    heading_level: Optional[int] = None
    page_number: int = 1


class ParsedDocument(BaseModel):
    title: str
    elements: List[ParsedElement]
    raw_markdown: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProvenanceRecord(BaseModel):
    """
    Tracks origin and lineage of parsed assets for compliance/audit trails.
    """
    document_id: int
    page: Optional[int] = None
    section: Optional[str] = None
    parser: str
    extraction_method: str  # e.g., "docling", "ocr_tesseract", "regex_rules"
    confidence: float = 1.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LayoutTreeNode(BaseModel):
    """
    Preserves hierarchical layout trees of documents instead of flat structure.
    """
    node_id: str
    type: str  # heading, paragraph, table, list, code, email_header, log_entry, diagram
    text: str
    page_numbers: List[int] = Field(default_factory=list)
    bounding_box: Optional[List[float]] = None  # [x, y, width, height]
    confidence: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    children: List["LayoutTreeNode"] = Field(default_factory=list)


# Support self-referential Pydantic schemas in Pydantic v2
LayoutTreeNode.model_rebuild()


class ParserResult(BaseModel):
    """
    Unified return object returned by every pluggable parser.
    """
    title: str
    layout_root: LayoutTreeNode
    raw_markdown: str
    file_type: str
    word_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    extras: Dict[str, Any] = Field(default_factory=dict)


class ExtractedEntity(BaseModel):
    name: str
    label: str  # Machine, Component, Employee, Department, Location, SafetyStandard, ComplianceReference, Risk
    metadata: Dict[str, Any] = Field(default_factory=dict)
    provenance: Optional[ProvenanceRecord] = None


class ExtractedRelationship(BaseModel):
    source: str
    target: str
    type: str  # connected_to, follows, maintains, applies_to, governs, located_in, contains
    metadata: Dict[str, Any] = Field(default_factory=dict)
    provenance: Optional[ProvenanceRecord] = None


class SemanticChunkPayload(BaseModel):
    chunk_id: str
    parent_doc_id: int
    section: str
    heading_hierarchy: List[str]
    page_numbers: List[int]
    token_count: int
    text: str
    # Persisted metadata for vector indexing (e.g. dimensions, checksum, model info)
    embedding_metadata: Dict[str, Any] = Field(default_factory=dict)


class EmbeddingDocument(BaseModel):
    """
    Embedding-ready payload prepared at the end of the ingestion pipeline.
    """
    chunk_id: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    entities: List[ExtractedEntity] = Field(default_factory=list)
    relationships: List[ExtractedRelationship] = Field(default_factory=list)
    provenance: Optional[ProvenanceRecord] = None


class IngestionReport(BaseModel):
    """
    Summarizes parsing operations, latencies, and counts for UI and observability.
    """
    parser_name: str
    modality_detected: str
    parse_latency_ms: float
    character_count: int
    chunk_count: int
    entity_count: int
    relationship_count: int
    average_confidence: float
    warnings: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentProfile(BaseModel):
    """
    Standardized profile representing document understanding and classification results.
    """
    title: str
    doc_type: str
    summary: str
    language: str
    keywords: List[str] = Field(default_factory=list)
    stats: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    extras: Dict[str, Any] = Field(default_factory=dict)


class ProcessedDocumentPayload(BaseModel):
    """
    Consolidated payload storing the outputs of the entire ingestion stages.
    """
    title: str
    summary: str
    keywords: List[str]
    language: str
    doc_type: str
    stats: Dict[str, Any]
    metadata: Dict[str, Any]
    layout_root: LayoutTreeNode
    chunks: List[SemanticChunkPayload]
    embedding_documents: List[EmbeddingDocument] = Field(default_factory=list)
    entities: List[ExtractedEntity] = Field(default_factory=list)
    relationships: List[ExtractedRelationship] = Field(default_factory=list)
    report: IngestionReport
    profile: DocumentProfile
