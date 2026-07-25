from fastapi import APIRouter
from app.services.processing.docling_service import docling_service
from app.services.processing.parser_registry import parser_registry

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health_check():
    """
    Service health check endpoint returning system connectivity and parser observability metrics.
    """
    metrics = docling_service.get_metrics()
    metrics.update({
        "status": "healthy",
        "service": "IndustryBrain-AI Backend API",
        "active_parsers": [p.__class__.__name__ for p in parser_registry.parsers]
    })
    return metrics
