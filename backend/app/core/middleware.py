"""
Core FastAPI middleware definitions re-exported from app.middleware.
"""
from app.middleware.correlation import CorrelationIdMiddleware

__all__ = ["CorrelationIdMiddleware"]
