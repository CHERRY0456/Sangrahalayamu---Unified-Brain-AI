from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class EmployeeProfileResponse(BaseModel):
    employeeId: str = Field(..., serialization_alias="employeeId")
    name: str
    email: str
    department: str
    designation: str
    avatarUrl: Optional[str] = Field(None, serialization_alias="avatarUrl")

    class Config:
        populate_by_name = True
        from_attributes = True

class SidebarItemSchema(BaseModel):
    label: str
    path: str
    icon: str

class QuickActionSchema(BaseModel):
    label: str
    actionUrl: str = Field(..., serialization_alias="actionUrl")
    isPlaceholder: Optional[bool] = Field(None, serialization_alias="isPlaceholder")

    class Config:
        populate_by_name = True

class WorkspaceManifestResponse(BaseModel):
    sidebar: List[SidebarItemSchema]
    dashboard: List[str]
    chatSuggestions: List[str] = Field(..., serialization_alias="chatSuggestions")
    transparencyFocus: str = Field(..., serialization_alias="transparencyFocus")
    quickActions: List[QuickActionSchema] = Field(..., serialization_alias="quickActions")
    defaultRoute: str = Field(..., serialization_alias="defaultRoute")

    class Config:
        populate_by_name = True

class UserMeResponse(BaseModel):
    profile: EmployeeProfileResponse
    permissions: List[str]
    manifest: WorkspaceManifestResponse

    class Config:
        populate_by_name = True

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

