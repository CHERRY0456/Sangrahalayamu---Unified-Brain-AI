"""
app/lifespan.py — Application Startup & Shutdown Lifecycle (Ticket #13)
========================================================================
Replaces the previous stub.  Responsibilities:

Startup
-------
1. Optional ENABLE_STARTUP_VALIDATION — fail fast on critical config gaps
2. Register all SQLAlchemy models in Base.metadata
3. Run database schema bootstrap (create_all)
4. Call ServiceRegistry.initialize() — registers every service AND emits
   the formatted startup diagnostics report to the log
5. Log a concise startup summary

Shutdown
--------
1. Call ServiceRegistry.shutdown() — graceful resource release
2. Log stop confirmation
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger("sangrahalayamu.lifespan")


def _validate_configuration() -> None:
    """
    Fail-fast check for critical environment variables.
    Called before any service is initialised.
    Raises ConfigurationError if required config is absent.
    """
    from app.core.config import settings
    from app.exceptions import ConfigurationError

    errors: list[str] = []

    if not settings.app.secret_key or len(settings.app.secret_key) < 32:
        errors.append("SECRET_KEY is missing or shorter than 32 characters.")
    if not settings.database.url:
        errors.append("DATABASE_URL is not configured.")
    if settings.llm.provider not in ("bedrock", "openai", "anthropic", "qwen"):
        errors.append(f"LLM_PROVIDER '{settings.llm.provider}' is not a recognised provider.")
    if settings.notifications.provider not in ("in_app", "email", "slack", "teams"):
        errors.append(f"NOTIFICATION_PROVIDER '{settings.notifications.provider}' is not recognised.")

    if errors:
        msg = "Startup validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        logger.critical(msg)
        raise ConfigurationError(msg)

    logger.info("[Lifespan] Configuration validation passed.")


def _bootstrap_database() -> None:
    """Register all models and run create_all for schema bootstrap."""
    from app.database.postgres import engine, Base

    # Ensure every model is imported so it registers on Base.metadata
    import app.database.base  # noqa: F401 — registers Role, User, Session, Document, etc.
    import app.models.audit_log    # noqa: F401 — registers AuditLog
    import app.models.notification # noqa: F401 — registers Notification, UserNotificationPreference

    Base.metadata.create_all(bind=engine)
    logger.info("[Lifespan] Database schema bootstrapped.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Everything before `yield` runs at startup; after `yield` at shutdown.
    """
    from app.core.config import settings
    from app.service_registry import ServiceRegistry

    logger.info(
        f"[Lifespan] Starting {settings.app.name} v{settings.app.version} ..."
    )

    # 1. Fail-fast validation
    if settings.flags.enable_startup_validation:
        _validate_configuration()

    # 2. Database schema
    _bootstrap_database()

    # 3. Service registry — also emits the startup diagnostics report
    ServiceRegistry.initialize()

    logger.info(
        f"[Lifespan] {settings.app.name} v{settings.app.version} started successfully. "
        f"Ready: {ServiceRegistry.is_ready()}"
    )

    yield  # ← application runs here

    # 4. Graceful shutdown
    logger.info(f"[Lifespan] Shutting down {settings.app.name} ...")
    ServiceRegistry.shutdown()
    logger.info("[Lifespan] Shutdown complete.")
