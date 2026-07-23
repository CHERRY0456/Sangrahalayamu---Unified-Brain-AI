from typing import Dict, Any
from .base_agent import BaseAgent, AgentContext, AgentResult
from app.services.retrieval.graph_reasoning import graph_reasoning_engine

class RCAAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "RootCauseAnalysisAgent"
        
    @property
    def description(self) -> str:
        return "Analyzes incidents, traces causal chains, and identifies probable root causes."

    async def execute(self, context: AgentContext) -> AgentResult:
        incident_id = context.parameters.get("incident_id")
        if not incident_id:
            # Fallback heuristic: Try to find an incident ID in the query, or fail
            return AgentResult(
                agent_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                reasoning_summary="Missing 'incident_id' parameter for RCA analysis."
            )
            
        evidence = await graph_reasoning_engine.trace_causal_chain(start_incident_id=incident_id)
        
        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "causal_paths": [p.model_dump() for p in evidence.paths]
            },
            confidence=evidence.confidence_score,
            reasoning_summary=evidence.reasoning_summary
        )
