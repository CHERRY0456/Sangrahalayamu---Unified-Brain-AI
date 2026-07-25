"""
Abstract Base Parser & Universal Data Schemas for Industrial Ingestion.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ParsedTable(BaseModel):
    """Structured matrix extracted from PDFs or Spreadsheets."""
    title: str = "Table"
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    page_number: int = 1


class ParsedChunk(BaseModel):
    """Text chunk ready for vector embedding and Qdrant indexing."""
    content: str
    chunk_index: int
    page_number: int = 1
    section_heading: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ParsedDocument(BaseModel):
    """Universal Extracted Industrial Document Payload."""
    filename: str
    file_type: str  # pdf, docx, xlsx, pptx, dxf, msg, image
    raw_text: str
    chunks: List[ParsedChunk] = Field(default_factory=list)
    tables: List[ParsedTable] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Industrial Entity & Tag Discoveries
    equipment_tags: List[str] = Field(default_factory=list)       # P-101A, V-402, B-201
    process_parameters: List[Dict[str, Any]] = Field(default_factory=list) # {"tag": "V-402", "parameter": "temp", "limit": "150C"}
    regulatory_references: List[str] = Field(default_factory=list) # OISD-118, PESO, Factory Act


class BaseParser(ABC):
    """Abstract Base Class for format-specific industrial parsers."""

    @abstractmethod
    def parse(self, file_path: str, filename: str) -> ParsedDocument:
        """Parse given local file path and return structured ParsedDocument."""
        pass
