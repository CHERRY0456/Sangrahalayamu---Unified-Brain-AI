import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.models.user import User
from app.api.deps import get_current_user
from app.services.agents.agent_orchestrator import agent_orchestrator, AgentContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])

class AgentRequestPayload(BaseModel):
    query: str
    workspace_id: str
    parameters: Dict[str, Any] = {}

@router.post("/rca", response_model=Dict[str, Any])
async def trigger_rca_agent(
    payload: AgentRequestPayload,
    current_user: User = Depends(get_current_user)
):
    """Triggers Root Cause Analysis Agent directly."""
    ctx = AgentContext(query=payload.query, workspace_id=payload.workspace_id, user_id=current_user.id, parameters=payload.parameters)
    results = await agent_orchestrator.execute_agents(ctx, agent_names=["RootCauseAnalysisAgent"])
    return {"results": [r.model_dump() for r in results]}

@router.post("/compliance", response_model=Dict[str, Any])
async def trigger_compliance_agent(
    payload: AgentRequestPayload,
    current_user: User = Depends(get_current_user)
):
    """Triggers Compliance Agent directly."""
    ctx = AgentContext(query=payload.query, workspace_id=payload.workspace_id, user_id=current_user.id, parameters=payload.parameters)
    results = await agent_orchestrator.execute_agents(ctx, agent_names=["ComplianceAgent"])
    return {"results": [r.model_dump() for r in results]}

@router.post("/failure", response_model=Dict[str, Any])
async def trigger_failure_agent(
    payload: AgentRequestPayload,
    current_user: User = Depends(get_current_user)
):
    """Triggers Failure Intelligence Agent directly."""
    ctx = AgentContext(query=payload.query, workspace_id=payload.workspace_id, user_id=current_user.id, parameters=payload.parameters)
    results = await agent_orchestrator.execute_agents(ctx, agent_names=["FailureIntelligenceAgent"])
    return {"results": [r.model_dump() for r in results]}
