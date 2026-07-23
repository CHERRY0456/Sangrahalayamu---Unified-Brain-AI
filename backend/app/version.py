"""
Platform version constants — single source of truth.
Read by /version endpoint and included in PlatformResponse.metadata.
"""
from app.core.config import settings

APP_VERSION   = settings.app.version
PLATFORM_NAME = settings.app.name
BUILD_DATE    = "2026-07-22"
API_PREFIX    = settings.app.api_prefix

VERSION_INFO = {
    "version":  APP_VERSION,
    "platform": PLATFORM_NAME,
    "build_date": BUILD_DATE,
    "api_prefix": API_PREFIX,
    "supported_features": [
        "authentication",
        "document_upload",
        "hybrid_retrieval",
        "ai_orchestration",
        "transparency_engine",
        "recommendation_engine",
        "audit_history",
        "notification_service",
    ],
}
