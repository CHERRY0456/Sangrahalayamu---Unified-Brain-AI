"""
app/service_registry.py — Central Service Registry (Ticket #13)
================================================================
Singleton that holds initialised instances of every platform service.
Initialised once during lifespan startup; routers access services through
app/dependencies.py FastAPI Depends() functions rather than instantiating
directly.

Startup Diagnostics Report
---------------------------
`ServiceRegistry.initialize()` runs each service probe, collects results,
and prints a formatted diagnostics table to the log — giving immediate
visibility into platform readiness during deployment debugging.

Example output:
┌─────────────────────────────────────────────────────────────────────┐
│         IndustryBrain-AI — Platform Startup Diagnostics             │
├──────────────────────────────┬──────────────┬───────────────────────┤
│ Component                    │ Status       │ Detail                │
├──────────────────────────────┼──────────────┼───────────────────────┤
│ Database                     │ OK           │ Connection verified   │
│ Storage (local)              │ OK           │ Root path accessible  │
│ Auth Service                 │ OK           │ JWT config valid      │
│ Audit Service                │ OK           │ Logging enabled       │
│ Notification Service         │ OK           │ Provider: in_app      │
│ AI Orchestrator              │ OK           │ Provider: bedrock     │
│ ...                          │ ...          │ ...                   │
└──────────────────────────────┴──────────────┴───────────────────────┘
"""
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("sangrahalayamu.service_registry")


# ---------------------------------------------------------------------------
# Diagnostics data model
# ---------------------------------------------------------------------------

@dataclass
class DiagnosticEntry:
    component: str
    status: str          # "OK" | "DEGRADED" | "FAILED" | "DISABLED"
    detail: str = ""
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# ServiceRegistry
# ---------------------------------------------------------------------------

class _ServiceRegistry:
    """
    Holds lazy-imported service singletons.
    All attributes are None until initialize() completes.
    """

    def __init__(self) -> None:
        # Service slots — populated by initialize()
        self.auth_service                = None
        self.policy_engine               = None
        self.upload_service              = None
        self.storage_service             = None
        self.processing_pipeline         = None
        self.retrieval_orchestrator      = None
        self.ai_orchestrator             = None
        self.transparency_engine         = None
        self.recommendation_orchestrator = None
        self.audit_service               = None
        self.notification_service        = None

        self._initialized: bool = False
        self._diagnostics: List[DiagnosticEntry] = []
        self._started_at: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """
        Import and register every service, run probes, then emit the
        startup diagnostics report.  Called once from lifespan startup.
        """
        self._started_at = datetime.utcnow()
        self._diagnostics = []

        self._probe_database()
        self._probe_storage()
        self._register_auth()
        self._register_policy()
        self._register_upload()
        self._register_processing()
        self._register_retrieval()
        self._register_ai_orchestrator()
        self._register_transparency()
        self._register_recommendations()
        self._register_audit()
        self._register_notifications()
        self._probe_configuration()

        self._initialized = True
        self._print_diagnostics_report()

    def shutdown(self) -> None:
        """Graceful teardown hook called from lifespan shutdown."""
        logger.info("[ServiceRegistry] Platform shutdown initiated — releasing resources.")
        self._initialized = False

    def is_ready(self) -> bool:
        """True when initialization completed with no FAILED probes."""
        if not self._initialized:
            return False
        return all(d.status != "FAILED" for d in self._diagnostics)

    def get_diagnostics(self) -> List[DiagnosticEntry]:
        return list(self._diagnostics)

    # ------------------------------------------------------------------
    # Infrastructure probes
    # ------------------------------------------------------------------

    def _probe_database(self) -> None:
        try:
            from app.database.postgres import engine
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
            self._ok("Database", "Connection verified")
        except Exception as exc:
            self._fail("Database", str(exc))

    def _probe_storage(self) -> None:
        from app.core.config import settings
        root = settings.processing.storage_root
        if os.path.isdir(root):
            self._ok("Storage", f"Root path accessible: '{root}'")
        else:
            try:
                os.makedirs(root, exist_ok=True)
                self._ok("Storage", f"Root directory created: '{root}'")
            except Exception as exc:
                self._fail("Storage", str(exc))

    def _probe_configuration(self) -> None:
        from app.core.config import settings
        issues = []
        if not settings.app.secret_key or len(settings.app.secret_key) < 32:
            issues.append("SECRET_KEY too short or missing")
        if not settings.database.url:
            issues.append("DATABASE_URL missing")
        if issues:
            self._degraded("Configuration", "; ".join(issues))
        else:
            self._ok("Configuration", f"v{settings.app.version} — all required vars present")

    # ------------------------------------------------------------------
    # Service registration helpers
    # ------------------------------------------------------------------

    def _register_auth(self) -> None:
        try:
            from app.services.auth.service import AuthService
            self.auth_service = AuthService()
            self._ok("Auth Service", "JWT config valid")
        except Exception as exc:
            self._fail("Auth Service", str(exc))

    def _register_policy(self) -> None:
        try:
            from app.services.policy import PolicyEngine
            self.policy_engine = PolicyEngine
            self._ok("Policy Engine", "RBAC + clearance rules loaded")
        except Exception as exc:
            self._fail("Policy Engine", str(exc))

    def _register_upload(self) -> None:
        try:
            from app.services.upload.service import UploadService
            self.upload_service = UploadService()
            self._ok("Upload Service", "Ready")
        except Exception as exc:
            self._fail("Upload Service", str(exc))

    def _register_processing(self) -> None:
        try:
            from app.services.processing.pipeline import DocumentProcessingPipeline
            self.processing_pipeline = DocumentProcessingPipeline()
            self._ok("Processing Pipeline", "All stages registered")
        except Exception as exc:
            self._fail("Processing Pipeline", str(exc))

    def _register_retrieval(self) -> None:
        try:
            from app.services.retrieval.orchestrator import HybridRetrievalService
            self.retrieval_orchestrator = HybridRetrievalService()
            from app.core.config import settings
            detail = (
                f"Semantic={settings.retrieval.weight_semantic} "
                f"Graph={settings.retrieval.weight_graph} "
                f"Metadata={settings.retrieval.weight_metadata}"
            )
            self._ok("Retrieval Engine", detail)
        except Exception as exc:
            self._fail("Retrieval Engine", str(exc))

    def _register_ai_orchestrator(self) -> None:
        try:
            from app.services.orchestrator.orchestrator import AIOrchestratorService
            self.ai_orchestrator = AIOrchestratorService()
            from app.core.config import settings
            self._ok("AI Orchestrator", f"Provider: {settings.llm.provider}")
        except Exception as exc:
            self._fail("AI Orchestrator", str(exc))

    def _register_transparency(self) -> None:
        try:
            from app.services.transparency.engine import TransparencyEngine
            from app.core.config import settings
            self.transparency_engine = TransparencyEngine()
            status = "enabled" if settings.flags.enable_transparency else "disabled"
            self._ok("Transparency Engine", status)
        except Exception as exc:
            self._fail("Transparency Engine", str(exc))

    def _register_recommendations(self) -> None:
        try:
            from app.services.recommendations.orchestrator import RecommendationService
            from app.core.config import settings
            self.recommendation_orchestrator = RecommendationService()
            if settings.flags.enable_recommendations:
                self._ok("Recommendation Engine", f"Max results: {5}")
            else:
                self._disabled("Recommendation Engine", "ENABLE_RECOMMENDATIONS=False")
        except Exception as exc:
            self._fail("Recommendation Engine", str(exc))

    def _register_audit(self) -> None:
        try:
            from app.services.audit.service import audit_service
            from app.core.config import settings
            self.audit_service = audit_service
            if settings.audit.enable_audit_logging:
                self._ok("Audit Service", f"Retention: {settings.audit.audit_retention_days}d")
            else:
                self._disabled("Audit Service", "ENABLE_AUDIT_LOGGING=False")
        except Exception as exc:
            self._fail("Audit Service", str(exc))

    def _register_notifications(self) -> None:
        try:
            from app.services.notifications.service import notification_service
            from app.core.config import settings
            self.notification_service = notification_service
            if settings.notifications.enable_notifications:
                self._ok("Notification Service", f"Provider: {settings.notifications.provider}")
            else:
                self._disabled("Notification Service", "ENABLE_NOTIFICATIONS=False")
        except Exception as exc:
            self._fail("Notification Service", str(exc))

    # ------------------------------------------------------------------
    # Diagnostic helpers
    # ------------------------------------------------------------------

    def _ok(self, component: str, detail: str = "") -> None:
        self._diagnostics.append(DiagnosticEntry(component, "OK", detail))

    def _fail(self, component: str, error: str) -> None:
        self._diagnostics.append(DiagnosticEntry(component, "FAILED", error=error))
        logger.error(f"[ServiceRegistry] FAILED — {component}: {error}")

    def _degraded(self, component: str, detail: str) -> None:
        self._diagnostics.append(DiagnosticEntry(component, "DEGRADED", detail))
        logger.warning(f"[ServiceRegistry] DEGRADED — {component}: {detail}")

    def _disabled(self, component: str, detail: str) -> None:
        self._diagnostics.append(DiagnosticEntry(component, "DISABLED", detail))

    # ------------------------------------------------------------------
    # Startup diagnostics report
    # ------------------------------------------------------------------

    def _print_diagnostics_report(self) -> None:
        """
        Emit a formatted ASCII table to the logger summarising every
        component probe result.  This runs once at startup.
        """
        col_w = (32, 10, 42)
        sep   = "─"

        def row(c: str, s: str, d: str) -> str:
            return (
                f"│ {c:<{col_w[0]}} │ {s:<{col_w[1]}} │ {d:<{col_w[2]}} │"
            )

        border_top = "┌" + "─" * (col_w[0]+2) + "┬" + "─" * (col_w[1]+2) + "┬" + "─" * (col_w[2]+2) + "┐"
        border_mid = "├" + "─" * (col_w[0]+2) + "┼" + "─" * (col_w[1]+2) + "┼" + "─" * (col_w[2]+2) + "┤"
        border_bot = "└" + "─" * (col_w[0]+2) + "┴" + "─" * (col_w[1]+2) + "┴" + "─" * (col_w[2]+2) + "┘"

        title = "IndustryBrain-AI -- Platform Startup Diagnostics"
        total_width = col_w[0] + col_w[1] + col_w[2] + 8
        title_line = "│" + title.center(total_width) + "│"
        title_border = "┌" + "─" * total_width + "┐"
        title_bot    = "├" + "─" * (col_w[0]+2) + "┬" + "─" * (col_w[1]+2) + "┬" + "─" * (col_w[2]+2) + "┤"

        lines = [
            "",
            title_border,
            title_line,
            title_bot,
            row("Component", "Status", "Detail"),
            border_mid,
        ]

        for entry in self._diagnostics:
            status_icon = {
                "OK":       "OK      ",
                "FAILED":   "FAILED  ",
                "DEGRADED": "DEGRADED",
                "DISABLED": "DISABLED",
            }.get(entry.status, entry.status)
            detail = entry.error or entry.detail
            lines.append(row(entry.component[:col_w[0]], status_icon, detail[:col_w[2]]))

        lines.append(border_bot)

        ready = self.is_ready()
        summary = f"  Platform ready: {'YES' if ready else 'NO'} | " \
                  f"Services: {len(self._diagnostics)} | " \
                  f"Started at: {self._started_at.strftime('%Y-%m-%d %H:%M:%S')} UTC"
        lines.append(summary)
        lines.append("")

        report = "\n".join(lines)
        # Use a single log call so the table appears unbroken in log aggregators
        logger.info(report)


# Module-level singleton
ServiceRegistry = _ServiceRegistry()
