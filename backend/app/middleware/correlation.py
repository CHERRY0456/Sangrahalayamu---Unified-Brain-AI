import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("sangrahalayamu.middleware.correlation")

class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Enterprise Correlation ID Middleware.
    
    Inspects or generates a unique `X-Request-ID` header for incoming HTTP requests,
    attaching it to request headers and response headers for trace correlation across logs.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Attach request_id to request state
        request.state.request_id = request_id
        
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
