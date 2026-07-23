from typing import Dict, Any
from .base_agent import BaseAgent, AgentContext, AgentResult
from app.services.retrieval.graph_reasoning import graph_reasoning_engine

class ComplianceAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "ComplianceAgent"
        
    @property
    def description(self) -> str:
        return "Detects compliance violations, verifies procedures, and maps regulations."

    async def execute(self, context: AgentContext) -> AgentResult:
        equipment_id = context.parameters.get("equipment_id")
        regulation_id = context.parameters.get("regulation_id")
        
        if not equipment_id or not regulation_id:
            return AgentResult(
                agent_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                reasoning_summary="Missing equipment or regulation parameters."
            )
            
        evidence = await graph_reasoning_engine.analyze_compliance_chain(equipment_id, regulation_id)
        
        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "compliance_paths": [p.model_dump() for p in evidence.paths]
            },
            confidence=evidence.confidence_score,
            reasoning_summary=evidence.reasoning_summary
        )
