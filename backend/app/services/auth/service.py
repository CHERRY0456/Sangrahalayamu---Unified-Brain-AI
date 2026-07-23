from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.models.role import Role
from app.core.security import verify_password
from app.schemas.auth import (
    UserLoginRequest, 
    TokenResponse, 
    UserMeResponse, 
    EmployeeProfileResponse, 
    WorkspaceManifestResponse
)
from .jwt import JwtService
from .session import SessionService
from .password import PasswordService

# Role-Based Workspace Configuration Manifest templates matching frontend config mapping
PERSONA_MANIFESTS = {
    'Field Technician': {
        'sidebar': [
            {'label': 'Dashboard', 'path': '/dashboard', 'icon': 'LayoutDashboard'},
            {'label': 'AI Chat', 'path': '/chat', 'icon': 'MessageSquare'},
            {'label': 'History', 'path': '/history', 'icon': 'History'},
        ],
        'dashboard': ['assigned-equipment', 'recent-repairs', 'safety-alerts', 'equipment-history', 'recent-uploads', 'my-requests'],
        'chatSuggestions': [
            'Show repair procedure for Boiler Cylinder B-3',
            'What is the equipment safety check for Loop-A?',
            'Check maintenance history logs on SV-901',
        ],
        'transparencyFocus': 'Safety standards, operation checklists, blueprint schematics, and operator manuals.',
        'quickActions': [
            {'label': 'View Repair Procedure', 'actionUrl': '/chat', 'isPlaceholder': True},
            {'label': 'Equipment History Logs', 'actionUrl': '/history'},
            {'label': 'Safety Guidelines Checklist', 'actionUrl': '/chat', 'isPlaceholder': True},
        ],
        'defaultRoute': '/dashboard'
    },
    'Maintenance Engineer': {
        'sidebar': [
            {'label': 'Dashboard', 'path': '/dashboard', 'icon': 'LayoutDashboard'},
            {'label': 'Upload Files', 'path': '/upload', 'icon': 'UploadCloud'},
            {'label': 'AI Processing', 'path': '/processing', 'icon': 'Cpu'},
            {'label': 'AI Chat', 'path': '/chat', 'icon': 'MessageSquare'},
            {'label': 'RAG Audit', 'path': '/transparency', 'icon': 'Eye'},
            {'label': 'History', 'path': '/history', 'icon': 'History'},
        ],
        'dashboard': ['failure-trends', 'maintenance-schedule', 'uploaded-manuals', 'processing-queue', 'recent-uploads', 'my-requests'],
        'chatSuggestions': [
            'Analyze root cause for Cylinder B-3 error codes',
            'Verify last failure schedule on primary loops',
            'Search OEM manual specs for turbine valve calibration',
        ],
        'transparencyFocus': 'Root cause resolution, entity relations, processing indexes, and full pipeline chronologies.',
        'quickActions': [
            {'label': 'Failure Analysis Review', 'actionUrl': '/transparency'},
            {'label': 'Inspection Log entries', 'actionUrl': '/history'},
            {'label': 'Ingest OEM Manual', 'actionUrl': '/upload'},
            {'label': 'Maintenance Schedule', 'actionUrl': '/chat', 'isPlaceholder': True},
        ],
        'defaultRoute': '/dashboard'
    },
    'Project Manager': {
        'sidebar': [
            {'label': 'Dashboard', 'path': '/dashboard', 'icon': 'LayoutDashboard'},
            {'label': 'AI Chat', 'path': '/chat', 'icon': 'MessageSquare'},
            {'label': 'RAG Audit', 'path': '/transparency', 'icon': 'Eye'},
            {'label': 'History', 'path': '/history', 'icon': 'History'},
        ],
        'dashboard': ['project-status', 'team-progress', 'project-delays', 'resource-allocation', 'recent-uploads', 'my-requests'],
        'chatSuggestions': [
            'What is the current project progress on Reactor Loop Q3?',
            'Check operational resource allocation constraints',
            'Summarize safety delays reported this week',
        ],
        'transparencyFocus': 'Milestone dependencies, project schedules, metadata summary tags, and team progress metrics.',
        'quickActions': [
            {'label': 'Project Progress Tracker', 'actionUrl': '/history'},
            {'label': 'Resource Allocation table', 'actionUrl': '/chat', 'isPlaceholder': True},
            {'label': 'Weekly Summary Reports', 'actionUrl': '/chat', 'isPlaceholder': True},
            {'label': 'Risk Heatmap audit', 'actionUrl': '/transparency'},
        ],
        'defaultRoute': '/dashboard'
    },
    'Regulatory & Compliance Manager': {
        'sidebar': [
            {'label': 'Dashboard', 'path': '/dashboard', 'icon': 'LayoutDashboard'},
            {'label': 'RAG Audit', 'path': '/transparency', 'icon': 'Eye'},
            {'label': 'Audit Logs', 'path': '/audit', 'icon': 'ShieldCheck'},
            {'label': 'History', 'path': '/history', 'icon': 'History'},
        ],
        'dashboard': ['pending-audits', 'compliance-status', 'access-requests', 'transparency-reviews', 'recent-uploads'],
        'chatSuggestions': [
            'Verify steam venting compliance guidelines OSHA 1910.111',
            'Review missing safety evidence for Cylinder B-3',
            'List regulatory requirements active for Reactor Unit 5',
        ],
        'transparencyFocus': 'Trace citation page intervals, verification standards, access permissions, and audit logs.',
        'quickActions': [
            {'label': 'Pending Compliance Audits', 'actionUrl': '/audit'},
            {'label': 'Compliance Policy Checklist', 'actionUrl': '/transparency'},
            {'label': 'Identify Missing Evidence Chunks', 'actionUrl': '/history'},
            {'label': 'Access Requests queues', 'actionUrl': '/audit'},
        ],
        'defaultRoute': '/dashboard'
    },
    'Director / Executive': {
        'sidebar': [
            {'label': 'Dashboard', 'path': '/dashboard', 'icon': 'LayoutDashboard'},
            {'label': 'AI Chat', 'path': '/chat', 'icon': 'MessageSquare'},
            {'label': 'RAG Audit', 'path': '/transparency', 'icon': 'Eye'},
            {'label': 'Audit Logs', 'path': '/audit', 'icon': 'ShieldCheck'},
            {'label': 'History', 'path': '/history', 'icon': 'History'},
        ],
        'dashboard': ['org-kpis', 'downtime-trends', 'ai-usage-analytics', 'risk-heatmap', 'knowledge-coverage', 'recent-uploads', 'access-requests'],
        'chatSuggestions': [
            'Summarize top operational risks across active plants',
            'Analyze downtime trends reported on Boiler 092',
            'Show organization KPIs and knowledge coverage metrics',
        ],
        'transparencyFocus': 'Business impact metrics, executive decisions, operational risk layers, and recommendations.',
        'quickActions': [
            {'label': 'Executive Operations Summary', 'actionUrl': '/chat', 'isPlaceholder': True},
            {'label': 'Operational Risk profiles', 'actionUrl': '/audit'},
            {'label': 'Downtime Trend analysis', 'actionUrl': '/transparency'},
            {'label': 'Organization Insights dashboards', 'actionUrl': '/history'},
        ],
        'defaultRoute': '/dashboard'
    }
}

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLoginRequest) -> TokenResponse:
        """
        Validates login parameters, verifies Argon2 hash matching, and issues new tokens.
        """
        # Find User
        stmt = select(User).where(User.email == login_data.email.lower().strip())
        user = db.scalar(stmt)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or account is inactive.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(user.hashed_password, login_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate tokens
        access_token, refresh_token = JwtService.generate_token_pair(user.id)
        
        # Save session tracking refresh token
        SessionService.create_session(db, user_id=user.id, refresh_token=refresh_token)

        # Emit audit compliance event (Ticket #11 constraint)
        try:
            from app.services.audit import audit_service, AuditEvent, EVENT_TYPE_AUTHENTICATION
            audit_service.record_event(db, AuditEvent(
                event_type=EVENT_TYPE_AUTHENTICATION,
                actor_id=user.id,
                actor_role=user.role.name if user.role else "User",
                action="login",
                status="SUCCESS",
                source_service="auth_service",
                metadata={"email": user.email}
            ))
        except Exception:
            pass

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    @staticmethod
    def rotate_tokens(db: Session, refresh_token: str) -> TokenResponse:
        """
        Validates a refresh token and yields a rotated token pair.
        """
        # 1. Validate signature & extract user_id subject
        user_id = JwtService.verify_token(refresh_token, is_refresh=True)

        # 2. Check session validity (revocation & expiration)
        if not SessionService.validate_session(db, refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is expired or revoked.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. Revoke current session
        SessionService.revoke_session(db, refresh_token)

        # 4. Generate new token pair and save new session
        access_token, new_refresh_token = JwtService.generate_token_pair(user_id)
        SessionService.create_session(db, user_id=user_id, refresh_token=new_refresh_token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token
        )

    @staticmethod
    def logout(db: Session, refresh_token: str) -> None:
        """
        Logs a user session out by revoking the refresh token tracker.
        """
        SessionService.revoke_session(db, refresh_token)

    @staticmethod
    def get_current_user_me(db: Session, user_id: int) -> UserMeResponse:
        """
        Resolves identity profile details and maps the user's role to its workspace configs.
        """
        stmt = select(User).where(User.id == user_id)
        user = db.scalar(stmt)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or inactive."
            )

        # Resolve role name & permissions
        role_name = user.role.name
        permissions = user.role.permissions

        # Get workspace manifest template based on role mapping
        manifest_data = PERSONA_MANIFESTS.get(role_name)
        if not manifest_data:
            # Fallback default manifest if role name is unmapped
            manifest_data = PERSONA_MANIFESTS['Field Technician']

        # Format profile response details
        profile_res = EmployeeProfileResponse(
            employeeId=user.employee_id,
            name=user.name,
            email=user.email,
            department=user.department,
            designation=user.designation
        )

        manifest_res = WorkspaceManifestResponse(
            sidebar=manifest_data['sidebar'],
            dashboard=manifest_data['dashboard'],
            chatSuggestions=manifest_data['chatSuggestions'],
            transparencyFocus=manifest_data['transparencyFocus'],
            quickActions=manifest_data['quickActions'],
            defaultRoute=manifest_data['defaultRoute']
        )

        return UserMeResponse(
            profile=profile_res,
            permissions=permissions,
            manifest=manifest_res
        )

    @staticmethod
    def forgot_password(db: Session, email: str) -> dict:
        """
        Generates a password reset token for the given email.
        Always returns success to prevent email enumeration attacks.
        In production, this would dispatch an email with the reset link.
        """
        import secrets
        import hashlib
        from datetime import timedelta
        from app.models.password_reset import PasswordResetToken

        stmt = select(User).where(User.email == email.lower().strip())
        user = db.scalar(stmt)

        if user and user.is_active:
            # Generate a secure random token
            raw_token = secrets.token_urlsafe(48)
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

            # Store hashed token with 1-hour expiry
            from datetime import datetime, timezone
            reset_entry = PasswordResetToken(
                token_hash=token_hash,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
                is_used=False,
                user_id=user.id,
            )
            db.add(reset_entry)
            db.commit()

            # In production: send email with link containing raw_token
            # For now, log it for development testing
            import logging
            logging.getLogger(__name__).info(
                f"Password reset token generated for {email}: {raw_token}"
            )

        # Always return success to prevent email enumeration
        return {"message": "If the email is registered, a password reset link has been sent."}

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> dict:
        """
        Validates a password reset token and updates the user's password.
        """
        import hashlib
        from datetime import datetime, timezone
        from app.models.password_reset import PasswordResetToken
        from app.core.security import hash_password

        token_hash = hashlib.sha256(token.encode()).hexdigest()

        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.is_used == False,
        )
        reset_entry = db.scalar(stmt)

        if not reset_entry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token."
            )

        if reset_entry.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            reset_entry.is_used = True
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired. Please request a new one."
            )

        # Validate password strength
        from app.services.auth.password import PasswordService
        PasswordService.validate_password_strength(new_password)

        # Update user's password
        user = db.get(User, reset_entry.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found."
            )

        user.hashed_password = hash_password(new_password)
        reset_entry.is_used = True
        db.commit()

        # Revoke all existing sessions for security
        from app.services.auth.session import SessionService
        SessionService.revoke_all_user_sessions(db, user.id)

        return {"message": "Password has been reset successfully. Please log in with your new password."}

