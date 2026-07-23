import logging
import asyncio
from typing import List, Dict, Any, Optional

from .base_agent import AgentContext, AgentResult
from .agent_registry import agent_registry
from .rca_agent import RCAAgent
from .compliance_agent import ComplianceAgent
from .failure_agent import FailureIntelligenceAgent
from .recommendation_agent import RecommendationAgent

logger = logging.getLogger(__name__)

# Register default agents
agent_registry.register(RCAAgent())
agent_registry.register(ComplianceAgent())
agent_registry.register(FailureIntelligenceAgent())
agent_registry.register(RecommendationAgent())

class AgentOrchestrator:
    """
    Coordinates execution of specialized enterprise AI agents.
    Supports parallel execution and result aggregation.
    """
    
    def determine_required_agents(self, query: str) -> List[str]:
        """
        Determines which agents should execute based on intent.
        In a full implementation, this could use an LLM router or fast text classification.
        For now, uses basic heuristics.
        """
        query_lower = query.lower()
        agents_to_run = []
        
        if "root cause" in query_lower or "incident" in query_lower:
            agents_to_run.append("RootCauseAnalysisAgent")
            
        if "compliance" in query_lower or "regulation" in query_lower or "violation" in query_lower:
            agents_to_run.append("ComplianceAgent")
            
        if "similar failure" in query_lower or "pattern" in query_lower:
            agents_to_run.append("FailureIntelligenceAgent")
            
        if "recommend" in query_lower or "best practice" in query_lower:
            agents_to_run.append("RecommendationAgent")
            
        return list(set(agents_to_run))

    async def execute_agents(self, context: AgentContext, agent_names: Optional[List[str]] = None) -> List[AgentResult]:
        """
        Executes specified agents (or auto-determines them) in parallel.
        """
        if not agent_names:
            agent_names = self.determine_required_agents(context.query)
            
        if not agent_names:
            logger.info("No specific agents triggered for query.")
            return []
            
        tasks = []
        for name in agent_names:
            try:
                agent = agent_registry.get_agent(name)
                tasks.append(agent.execute(context))
            except ValueError as e:
                logger.error(e)
                
        if not tasks:
            return []
            
        logger.info(f"Executing agents in parallel: {agent_names}")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_results = []
        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Agent execution failed: {res}")
            else:
                final_results.append(res)
                
        return final_results

agent_orchestrator = AgentOrchestrator()
