import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.api.deps import get_current_user
from app.services.agents.agent_orchestrator import agent_orchestrator, AgentContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/proactive", response_model=List[Dict[str, Any]])
async def get_proactive_recommendations(
    equipment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Fetches proactive recommendations by invoking the RecommendationAgent with equipment context.
    """
    ctx = AgentContext(
        query="Provide proactive maintenance recommendations.",
        workspace_id="default",
        user_id=current_user.id,
        parameters={"equipment_id": equipment_id}
    )
    results = await agent_orchestrator.execute_agents(ctx, agent_names=["RecommendationAgent"])
    return [r.model_dump() for r in results]
