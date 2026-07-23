"""
app/response_models.py — Unified API Response Contract (Ticket #13)
====================================================================
Every router returns a PlatformResponse[T].  No raw dicts, no
inconsistent shapes.

Usage:
    from app.response_models import ok, error, PlatformResponse

    @router.get("/things/{id}", response_model=PlatformResponse[ThingSchema])
    def get_thing(id: int):
        thing = ThingService.get(id)
        return ok(data=thing, message="Thing retrieved.")

    @router.post("/things", response_model=PlatformResponse[ThingSchema])
    def create_thing(body: ThingCreate):
        ...
        return error(errors=["Name already exists."], status_code=409)
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from fastapi import Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from app.context import RequestContext

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Core response envelope
# ---------------------------------------------------------------------------

class PlatformResponse(GenericModel, Generic[T]):
    """
    Standardised envelope wrapping every API response.

    Fields
    ------
    success      : True on 2xx, False on 4xx/5xx
    request_id   : Injected from RequestContext for end-to-end tracing
    timestamp    : UTC time the response was serialised
    data         : The typed payload (None on error responses)
    metadata     : Supplemental key/value pairs (pagination, counts, etc.)
    warnings     : Non-fatal notices the client should surface
    errors       : Human-readable error descriptions on failure
    """
    success:    bool
    request_id: Optional[str] = None
    timestamp:  datetime = Field(default_factory=datetime.utcnow)
    data:       Optional[T] = None
    metadata:   Dict[str, Any] = Field(default_factory=dict)
    warnings:   List[str] = Field(default_factory=list)
    errors:     List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Factory helpers — keeps router code clean
# ---------------------------------------------------------------------------

def ok(
    data: Any = None,
    *,
    message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    warnings: Optional[List[str]] = None,
) -> PlatformResponse:
    """Return a successful PlatformResponse, auto-injecting the current request_id."""
    return PlatformResponse(
        success=True,
        request_id=RequestContext.get_request_id(),
        data=data,
        metadata=metadata or {},
        warnings=warnings or [],
        errors=[],
    )


def error(
    errors: List[str],
    *,
    data: Any = None,
    metadata: Optional[Dict[str, Any]] = None,
    warnings: Optional[List[str]] = None,
) -> PlatformResponse:
    """Return a failure PlatformResponse."""
    return PlatformResponse(
        success=False,
        request_id=RequestContext.get_request_id(),
        data=data,
        metadata=metadata or {},
        warnings=warnings or [],
        errors=errors,
    )


def error_response(
    errors: List[str],
    status_code: int = 400,
    metadata: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """
    Return a FastAPI JSONResponse with the correct HTTP status code.
    Used inside exception handlers where returning a Pydantic model
    directly is not possible.
    """
    body = error(errors=errors, metadata=metadata or {})
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json"),
    )
