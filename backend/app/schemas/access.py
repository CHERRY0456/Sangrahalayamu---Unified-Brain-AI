from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class AccessRequestCreate(BaseModel):
    document_id: int = Field(..., serialization_alias="document_id")
    requested_sections: List[str] = Field(default_factory=lambda: ["Entire Document"], serialization_alias="requested_sections")
    justification: str = Field(..., min_length=5, max_length=500)

    class Config:
        populate_by_name = True

class AccessRequestReview(BaseModel):
    remarks: str = Field(..., min_length=2, max_length=500)
    valid_hours: Optional[int] = Field(24, description="Validity period in hours for approved overrides", serialization_alias="valid_hours")

    class Config:
        populate_by_name = True

class AccessRequestResponse(BaseModel):
    id: int
    requester_id: int = Field(..., serialization_alias="requester_id")
    requester_name: str = Field(..., serialization_alias="requester_name")
    requester_email: str = Field(..., serialization_alias="requester_email")
    document_id: int = Field(..., serialization_alias="document_id")
    document_name: str = Field(..., serialization_alias="document_name")
    requested_sections: List[str] = Field(..., serialization_alias="requested_sections")
    justification: str
    status: str
    created_at: datetime = Field(..., serialization_alias="created_at")
    updated_at: datetime = Field(..., serialization_alias="updated_at")

    class Config:
        populate_by_name = True
        from_attributes = True

class AccessRequestListResponse(BaseModel):
    requests: List[AccessRequestResponse]
