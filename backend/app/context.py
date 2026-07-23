"""
app/context.py — Platform-level RequestContext (Ticket #13)
============================================================
Single contextvars-backed store for per-request metadata.

Middleware populates this ONCE at the top of every request.
All downstream services (Audit, Notifications, AI Orchestrator,
Retrieval, Transparency) read from it without receiving these
values through method signatures.

Bridge to CorrelationContext
-----------------------------
On every `RequestContext.set()`, this module also calls
`CorrelationContext.set_context()` from services/audit/context.py
so that AuditEvent Pydantic default factories keep working
transparently — no changes to audit code required.
"""
import uuid
import contextvars
from datetime import datetime
from typing import Optional, Any, Dict

# ---------------------------------------------------------------------------
# Internal context variable — one dict per asyncio task / OS thread
# ---------------------------------------------------------------------------
_request_ctx: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
    "request_ctx", default={}
)


class RequestContext:
    """
    Platform-level per-request context manager.

    Usage (in middleware):
        token = RequestContext.set(
            request_id="...", session_id="...",
            actor_id=None, actor_role=None,
        )
        try:
            response = await call_next(request)
        finally:
            RequestContext.clear(token)

    Usage (in any service):
        ctx = RequestContext.get()
        rid = ctx.request_id
    """

    # ------------------------------------------------------------------ set/clear

    @staticmethod
    def set(
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        actor_id: Optional[int] = None,
        actor_role: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Any:
        """
        Populate the context for the current request scope.
        Returns the ContextVar token required to reset the context later.
        """
        rid = request_id or str(uuid.uuid4())
        cid = correlation_id or rid

        ctx = {
            "request_id":        rid,
            "session_id":        session_id,
            "actor_id":          actor_id,
            "actor_role":        actor_role,
            "correlation_id":    cid,
            "request_start_time": datetime.utcnow(),
        }
        token = _request_ctx.set(ctx)

        # Bridge: keep CorrelationContext (used by AuditEvent default factories) in sync
        try:
            from app.services.audit.context import CorrelationContext
            CorrelationContext.set_context(
                request_id=rid,
                session_id=session_id,
                actor_id=actor_id,
                actor_role=actor_role,
            )
        except Exception:
            pass  # Never let context bridging break the request

        return token

    @staticmethod
    def clear(token: Any) -> None:
        """Reset the context variable to its previous state using the token."""
        _request_ctx.reset(token)

    @staticmethod
    def update_actor(actor_id: int, actor_role: str) -> None:
        """
        Called by auth middleware/deps after JWT is verified to inject
        the authenticated user without re-populating the full context.
        """
        current = dict(_request_ctx.get())
        current["actor_id"]   = actor_id
        current["actor_role"] = actor_role
        _request_ctx.set(current)

        try:
            from app.services.audit.context import CorrelationContext
            CorrelationContext.update_actor(actor_id, actor_role)
        except Exception:
            pass

    # ------------------------------------------------------------------ read

    @staticmethod
    def get() -> "_ContextSnapshot":
        return _ContextSnapshot(_request_ctx.get())

    @staticmethod
    def get_request_id() -> Optional[str]:
        return _request_ctx.get().get("request_id")

    @staticmethod
    def get_session_id() -> Optional[str]:
        return _request_ctx.get().get("session_id")

    @staticmethod
    def get_actor_id() -> Optional[int]:
        return _request_ctx.get().get("actor_id")

    @staticmethod
    def get_actor_role() -> Optional[str]:
        return _request_ctx.get().get("actor_role")

    @staticmethod
    def get_correlation_id() -> Optional[str]:
        return _request_ctx.get().get("correlation_id")

    @staticmethod
    def get_start_time() -> Optional[datetime]:
        return _request_ctx.get().get("request_start_time")

    @staticmethod
    def elapsed_ms() -> float:
        start = _request_ctx.get().get("request_start_time")
        if start is None:
            return 0.0
        return (datetime.utcnow() - start).total_seconds() * 1000


class _ContextSnapshot:
    """Immutable snapshot of the current request context."""
    __slots__ = (
        "request_id", "session_id", "actor_id",
        "actor_role", "correlation_id", "request_start_time",
    )

    def __init__(self, data: Dict[str, Any]) -> None:
        self.request_id        = data.get("request_id")
        self.session_id        = data.get("session_id")
        self.actor_id          = data.get("actor_id")
        self.actor_role        = data.get("actor_role")
        self.correlation_id    = data.get("correlation_id")
        self.request_start_time = data.get("request_start_time")

    def as_dict(self) -> Dict[str, Any]:
        return {s: getattr(self, s) for s in self.__slots__}
