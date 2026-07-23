"""
app/exceptions.py — Domain Exceptions & Global Exception Handlers (Ticket #13)
================================================================================
Defines typed domain exceptions and maps them to standardised PlatformResponse
payloads with appropriate HTTP status codes.

Registration
------------
Exception handlers are registered in main.py:

    from app.exceptions import register_exception_handlers
    register_exception_handlers(app)
"""
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.response_models import error_response

logger = logging.getLogger("sangrahalayamu.exceptions")


# ---------------------------------------------------------------------------
# Domain exception hierarchy
# ---------------------------------------------------------------------------

class PlatformException(Exception):
    """Base class for all IndustryBrain-AI domain exceptions."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class PermissionDeniedError(PlatformException):
    """Raised when a user attempts an action they are not authorised to perform."""
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "You do not have permission to perform this action."


class AuthenticationError(PlatformException):
    """Raised when authentication credentials are missing or invalid."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Authentication is required."


class ResourceNotFoundError(PlatformException):
    """Raised when a requested resource does not exist."""
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "The requested resource was not found."


class DuplicateResourceError(PlatformException):
    """Raised when creating a resource that already exists."""
    status_code = status.HTTP_409_CONFLICT
    default_message = "A resource with the same identity already exists."


class ValidationFailedError(PlatformException):
    """Raised when business-rule validation fails (distinct from Pydantic schema errors)."""
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    default_message = "Request data failed validation."


class ProcessingError(PlatformException):
    """Raised when a document processing pipeline stage fails."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = "Document processing failed."


class AIProviderError(PlatformException):
    """Raised when the configured LLM provider returns an unrecoverable error."""
    status_code = status.HTTP_502_BAD_GATEWAY
    default_message = "The AI provider returned an error. Please try again."


class ConfigurationError(PlatformException):
    """Raised during startup when a required configuration is invalid or missing."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = "Platform configuration is invalid."


class StorageError(PlatformException):
    """Raised when the storage provider cannot read or write a document."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = "Storage operation failed."


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

def _log_exception(exc: Exception, request: Request) -> None:
    from app.context import RequestContext
    logger.error(
        f"[{type(exc).__name__}] {exc} | "
        f"path={request.url.path} | "
        f"request_id={RequestContext.get_request_id()}"
    )


async def _handle_platform_exception(request: Request, exc: PlatformException):
    _log_exception(exc, request)
    return error_response([exc.message], status_code=exc.status_code)


async def _handle_http_exception(request: Request, exc: StarletteHTTPException):
    logger.warning(
        f"[HTTPException] {exc.status_code} {exc.detail} | path={request.url.path}"
    )
    return error_response(
        errors=[str(exc.detail)],
        status_code=exc.status_code,
    )


async def _handle_validation_exception(request: Request, exc: RequestValidationError):
    """Convert Pydantic v2 validation errors into PlatformResponse format."""
    messages = [
        f"{' → '.join(str(loc) for loc in err['loc'])}: {err['msg']}"
        for err in exc.errors()
    ]
    logger.info(f"[ValidationError] {messages} | path={request.url.path}")
    return error_response(errors=messages, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)


async def _handle_generic_exception(request: Request, exc: Exception):
    _log_exception(exc, request)
    return error_response(
        errors=["An internal server error occurred. Please contact support."],
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI application instance."""
    app.add_exception_handler(PlatformException,        _handle_platform_exception)
    app.add_exception_handler(StarletteHTTPException,   _handle_http_exception)
    app.add_exception_handler(RequestValidationError,   _handle_validation_exception)
    app.add_exception_handler(Exception,                _handle_generic_exception)
    logger.info("[ExceptionHandlers] All domain exception handlers registered.")
