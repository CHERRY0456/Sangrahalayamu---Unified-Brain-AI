"""
app/middleware.py — Request Middleware Stack (Ticket #13)
=========================================================
Three middleware classes registered in main.py (innermost → outermost):

1. RequestCorrelationMiddleware
   - Reads or generates X-Request-ID and X-Session-ID headers
   - Calls RequestContext.set() to populate the platform context
   - Echoes X-Request-ID back on every response for client tracing
   - Clears context when the response is sent

2. RequestTimingMiddleware
   - Measures end-to-end handler duration
   - Adds X-Process-Time-Ms header to every response
   - Emits a structured log line after each request

3. (CORS handled by FastAPI built-in CORSMiddleware — stays in main.py)
"""
import logging
import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.context import RequestContext

logger = logging.getLogger("sangrahalayamu.middleware")


# ---------------------------------------------------------------------------
# 1. Request Correlation Middleware
# ---------------------------------------------------------------------------

class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """
    Generates or propagates X-Request-ID / X-Session-ID per request.
    Populates RequestContext (which bridges to CorrelationContext for Audit).
    Adds X-Request-ID to every response header for client-side tracing.
    """
    REQUEST_ID_HEADER  = "X-Request-ID"
    SESSION_ID_HEADER  = "X-Session-ID"
    CORRELATION_HEADER = "X-Correlation-ID"

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Honour caller-supplied IDs (useful for service-to-service calls)
        request_id    = request.headers.get(self.REQUEST_ID_HEADER)  or str(uuid.uuid4())
        session_id    = request.headers.get(self.SESSION_ID_HEADER)
        correlation_id = request.headers.get(self.CORRELATION_HEADER) or request_id

        # Populate platform context — bridges to CorrelationContext automatically
        token = RequestContext.set(
            request_id=request_id,
            session_id=session_id,
            correlation_id=correlation_id,
        )

        try:
            response: Response = await call_next(request)
        finally:
            RequestContext.clear(token)

        # Echo back so the client can correlate
        response.headers[self.REQUEST_ID_HEADER]  = request_id
        response.headers[self.CORRELATION_HEADER] = correlation_id
        return response


# ---------------------------------------------------------------------------
# 2. Request Timing Middleware
# ---------------------------------------------------------------------------

class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Measures wall-clock handler duration, appends X-Process-Time-Ms header,
    and emits a single structured log line per request.

    Log format:
        METHOD PATH  status=200  duration=14.3ms  request_id=...
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"

        logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} "
            f"duration={duration_ms:.1f}ms "
            f"request_id={RequestContext.get_request_id() or '-'}"
        )
        return response
