import contextvars
from typing import Optional, Dict, Any

# Thread/Asyncio safe context variables (Ticket #11 extension)
_correlation_context: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
    "correlation_context", default={}
)

class CorrelationContext:
    """
    Helper managing request-level correlation variables using ContextVars.
    """
    @staticmethod
    def set_context(
        request_id: str,
        session_id: Optional[str] = None,
        actor_id: Optional[int] = None,
        actor_role: Optional[str] = None
    ) -> Any:
        ctx = {
            "request_id": request_id,
            "session_id": session_id,
            "actor_id": actor_id,
            "actor_role": actor_role
        }
        return _correlation_context.set(ctx)

    @staticmethod
    def get_context() -> Dict[str, Any]:
        return _correlation_context.get()

    @staticmethod
    def clear_context(token: Any) -> None:
        """
        Resets context using token returned by set_context.
        """
        _correlation_context.reset(token)

    @staticmethod
    def update_actor(actor_id: int, actor_role: str) -> None:
        """
        Allows updating actor info after user is authenticated mid-request.
        """
        current = dict(_correlation_context.get())
        current["actor_id"] = actor_id
        current["actor_role"] = actor_role
        _correlation_context.set(current)

def get_ctx_request_id() -> Optional[str]:
    return _correlation_context.get().get("request_id")

def get_ctx_session_id() -> Optional[str]:
    return _correlation_context.get().get("session_id")

def get_ctx_actor_id() -> Optional[int]:
    return _correlation_context.get().get("actor_id")

def get_ctx_actor_role() -> Optional[str]:
    return _correlation_context.get().get("actor_role")
