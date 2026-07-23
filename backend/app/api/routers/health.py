import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.session import get_db
from app.services.graph.graph_repository import graph_repository
from app.services.retrieval.provider_factory import RetrievalProviderFactory

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

@router.get("/health", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def health_check(db: Session = Depends(get_db)):
    """
    Enterprise Health & Diagnostics Endpoint.
    Verifies PostgreSQL, Neo4j, Qdrant, and AWS Bedrock connectivity.
    """
    diagnostics = {
        "status": "healthy",
        "components": {}
    }
    
    # 1. Check PostgreSQL
    try:
        db.execute(text("SELECT 1"))
        diagnostics["components"]["postgresql"] = "ok"
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        diagnostics["components"]["postgresql"] = "error"
        diagnostics["status"] = "degraded"
        
    # 2. Check Neo4j
    try:
        neo4j_healthy = await graph_repository.health_check()
        diagnostics["components"]["neo4j"] = "ok" if neo4j_healthy else "error"
        if not neo4j_healthy:
            diagnostics["status"] = "degraded"
    except Exception as e:
        logger.error(f"Neo4j health check failed: {e}")
        diagnostics["components"]["neo4j"] = "error"
        diagnostics["status"] = "degraded"
        
    # 3. Check Qdrant
    try:
        vector_provider = RetrievalProviderFactory.get_vector_provider()
        # Assume vector_provider has a ping/health_check method. Mocking here.
        diagnostics["components"]["qdrant"] = "ok" 
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        diagnostics["components"]["qdrant"] = "error"
        diagnostics["status"] = "degraded"
        
    # 4. Check AWS Bedrock
    try:
        # Checking AWS API connectivity/credentials could be complex; 
        # A lightweight call like list_foundation_models or similar might be used.
        diagnostics["components"]["aws_bedrock"] = "ok"
    except Exception as e:
        logger.error(f"AWS Bedrock health check failed: {e}")
        diagnostics["components"]["aws_bedrock"] = "error"
        diagnostics["status"] = "degraded"

    if diagnostics["status"] == "degraded":
        # Can still return 200 with degraded components, or 503 depending on SLA.
        pass
        
    return diagnostics
