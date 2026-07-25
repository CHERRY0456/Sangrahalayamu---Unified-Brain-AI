"""
app/main.py — Application Entry Point (Ticket #13)
====================================================
Wires the complete middleware stack, exception handlers, and routers.
"""
import logging
import warnings

# Suppress PyTorch DataLoader pin_memory UserWarnings in CPU-only environments
warnings.filterwarnings("ignore", category=UserWarning, message=".*pin_memory.*")
warnings.filterwarnings("ignore", category=UserWarning, module=".*dataloader.*")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.lifespan import lifespan
from app.middleware import RequestCorrelationMiddleware, RequestTimingMiddleware
from app.exceptions import register_exception_handlers
from app.api.router import api_router
from app.api.routers.health import router as health_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app.name,
    description=(
        "IndustryBrain-AI — Enterprise Knowledge Intelligence Platform. "
        "Provides secure document retrieval, AI-powered Q&A, explainability, "
        "recommendations, audit, and notification services."
    ),
    version=settings.app.version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "health",          "description": "Platform liveness, readiness, and version."},
        {"name": "authentication",  "description": "Login, token refresh, and session management."},
        {"name": "upload",          "description": "Document upload and lifecycle management."},
        {"name": "access",          "description": "Temporary access override requests and approvals."},
        {"name": "search",          "description": "Hybrid semantic + graph retrieval."},
        {"name": "ai",              "description": "AI question answering and transparency reports."},
        {"name": "audit",           "description": "Compliance activity log and user history."},
        {"name": "notifications",   "description": "In-app notification management."},
        {"name": "administration",  "description": "Platform administration and diagnostics."},
    ],
)

# ---------------------------------------------------------------------------
# Middleware stack  (applied outermost → innermost, i.e., last registered runs first)
# ---------------------------------------------------------------------------

# 1. CORS — must be outermost so pre-flight OPTIONS requests are handled first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Timing — wraps the full handler after CORS is resolved
app.add_middleware(RequestTimingMiddleware)

# 3. Correlation — innermost; populates RequestContext before any handler runs
app.add_middleware(RequestCorrelationMiddleware)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

register_exception_handlers(app)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

# Health/readiness/version at root level (no API prefix) — for load balancers
app.include_router(health_router)

# All business routers under /api prefix
app.include_router(api_router, prefix=settings.app.api_prefix)
