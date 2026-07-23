# Import all models here so that Base metadata registers them correctly
from .postgres import Base
from app.models.role import Role
from app.models.user import User
from app.models.session import UserSession
from app.models.document import Document
from app.models.access_request import AccessRequest
from app.models.access_grant import AccessGrant
from app.models.approval_history import ApprovalHistory
from app.models.audit_log import AuditLog            # Ticket #11
from app.models.notification import (                # Ticket #12
    Notification, UserNotificationPreference
)
