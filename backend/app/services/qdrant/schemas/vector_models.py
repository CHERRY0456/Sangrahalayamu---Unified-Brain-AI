from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QdrantPayload(BaseModel):
    """
    Standardized payload for documents stored in Qdrant.
    Designed for strict metadata filtering and permission enforcement.
    """
    chunk_id: str = Field(..., description="Unique ID for the chunk")
    document_id: str = Field(..., description="Parent document ID")
    workspace_id: str = Field(..., description="Workspace ID for multi-tenant isolation")
    role_permissions: List[str] = Field(default_factory=list, description="Roles permitted to view this chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom document metadata")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Source provenance (URL, path, etc)")
    entities: List[str] = Field(default_factory=list, description="Extracted entities")
    relationships: List[str] = Field(default_factory=list, description="Extracted relationships")
    
class SearchResult(BaseModel):
    """
    Standardized return type for vector search results.
    """
    chunk_id: str
    score: float
    payload: QdrantPayload
