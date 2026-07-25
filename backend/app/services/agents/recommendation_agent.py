"""
RecommendationAgent disabled per enterprise requirement.
"""
from .base_agent import BaseAgent, AgentContext, AgentResult

class RecommendationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "RecommendationAgent"

    @property
    def description(self) -> str:
        return "Disabled Recommendation Agent."

    async def execute(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            success=False,
            data={},
            confidence=0.0,
            reasoning_summary="Recommendation Agent is disabled."
        )
