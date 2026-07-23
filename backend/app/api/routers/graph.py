import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.retrieval.graph_retrieval import graph_retrieval_engine
from app.services.graph.schemas.graph_models import GraphRelationship

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])

@router.get("/neighbors/{node_id}", response_model=List[Any])
async def get_neighbors(
    node_id: str,
    depth: int = Query(1, ge=1, le=3),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves adjacent nodes and relationships from the Graph Database.
    """
    relationships = await graph_retrieval_engine.get_related_assets(asset_id=node_id, depth=depth)
    return [r.model_dump() for r in relationships]

@router.get("/equipment/{equipment_id}/history", response_model=List[Any])
async def get_equipment_history(
    equipment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves maintenance history connections for specific equipment.
    """
    history = await graph_retrieval_engine.get_maintenance_history(equipment_id)
    return [r.model_dump() for r in history]

@router.get("/failures/{failure_mode_id}", response_model=List[Any])
async def get_similar_failures(
    failure_mode_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves similar failure patterns connected to a failure mode.
    """
    failures = await graph_retrieval_engine.get_similar_failures(failure_mode_id)
    return [r.model_dump() for r in failures]
