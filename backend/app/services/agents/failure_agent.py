from typing import Dict, Any
from .base_agent import BaseAgent, AgentContext, AgentResult
from app.services.retrieval.graph_reasoning import graph_reasoning_engine

class FailureIntelligenceAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "FailureIntelligenceAgent"
        
    @property
    def description(self) -> str:
        return "Discovers similar historical failures, identifies recurring patterns, and estimates impact."

    async def execute(self, context: AgentContext) -> AgentResult:
        failure_mode_id = context.parameters.get("failure_mode_id")
        
        if not failure_mode_id:
            return AgentResult(
                agent_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                reasoning_summary="Missing failure_mode_id parameter."
            )
            
        evidence = await graph_reasoning_engine.propagate_failure(failure_mode_id)
        
        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "impact_paths": [p.model_dump() for p in evidence.paths]
            },
            confidence=evidence.confidence_score,
            reasoning_summary=evidence.reasoning_summary
        )
