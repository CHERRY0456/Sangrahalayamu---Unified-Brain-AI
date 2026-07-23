from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .models import (
    ProcessedDocumentPayload,
    ExtractedEntity,
    ExtractedRelationship,
    SemanticChunkPayload,
    ParsedDocument
)

class PipelineContext(BaseModel):
    """
    Shared execution context containing intermediate properties and extracted assets.
    """
    document_id: int
    doc_uuid: str
    filename: str
    file_path: str
    uploader: Any  # Authenticated User model instance (typed as Any for SQLAlchemy validation bypass)
    
    # State values populated sequentially by stages
    parsed_doc: Optional[ParsedDocument] = None
    metadata: Optional[Dict[str, Any]] = None
    entities: Optional[List[ExtractedEntity]] = None
    relationships: Optional[List[ExtractedRelationship]] = None
    chunks: Optional[List[SemanticChunkPayload]] = None
    
    extra_state: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

class PipelineStage(ABC):
    """
    Common stage interface for processing operations (Parser, Metadata, Entity, Relationship, Chunker, Embedding).
    """
    @abstractmethod
    def execute(self, context: PipelineContext, db: Session) -> None:
        """
        Executes stage logic, reading from and writing findings into context.
        """
        pass
