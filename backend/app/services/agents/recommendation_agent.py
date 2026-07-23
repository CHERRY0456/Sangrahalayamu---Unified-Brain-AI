from typing import Dict, Any
from .base_agent import BaseAgent, AgentContext, AgentResult
from app.services.retrieval.graph_retrieval import graph_retrieval_engine

class RecommendationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "RecommendationAgent"
        
    @property
    def description(self) -> str:
        return "Generates recommendations based on similar maintenance history, failure patterns, and safety standards."

    async def execute(self, context: AgentContext) -> AgentResult:
        equipment_id = context.parameters.get("equipment_id")
        
        if not equipment_id:
            return AgentResult(
                agent_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                reasoning_summary="Missing equipment_id parameter."
            )
            
        history_rels = await graph_retrieval_engine.get_maintenance_history(equipment_id)
        
        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "maintenance_history": [r.model_dump() for r in history_rels]
            },
            confidence=0.85 if history_rels else 0.5,
            reasoning_summary="Recommendation baseline extracted from maintenance history."
        )
