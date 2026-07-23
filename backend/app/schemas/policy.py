from typing import Optional
from pydantic import BaseModel, Field

class PolicyDecision(BaseModel):
    allowed: bool = Field(..., description="Boolean indicating if access is granted")
    reason: str = Field(..., description="Human-readable explanation of the authorization outcome")
    required_permission: Optional[str] = Field(None, description="The permission identifier required for the action")
    required_clearance: Optional[str] = Field(None, description="The clearance tier level required for the document classification")
    user_clearance: Optional[str] = Field(None, description="The clearance tier level held by the requesting user")
    can_request_override: bool = Field(False, description="Flag indicating if the user has override eligibility for manual review request")
    audit_reason: Optional[str] = Field(None, description="Detailed trace reason code for security and compliance audits")
