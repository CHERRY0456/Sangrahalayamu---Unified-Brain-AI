from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class DocumentUploadResponse(BaseModel):
    id: int
    uuid: str
    name: str
    mime_type: str = Field(..., serialization_alias="mime_type")
    file_size: int = Field(..., serialization_alias="file_size")
    status: str
    classification: str
    required_clearance: str = Field(..., serialization_alias="required_clearance")
    department: str
    created_at: datetime = Field(..., serialization_alias="created_at")

    class Config:
        populate_by_name = True
        from_attributes = True

class DocumentListResponse(BaseModel):
    documents: List[DocumentUploadResponse]
