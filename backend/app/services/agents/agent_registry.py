from typing import Dict, List
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Registry for managing available enterprise agents.
    """
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        if agent.name in self._agents:
            logger.warning(f"Agent {agent.name} is already registered. Overwriting.")
        self._agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")

    def get_agent(self, name: str) -> BaseAgent:
        if name not in self._agents:
            raise ValueError(f"Agent '{name}' not found in registry.")
        return self._agents[name]

    def get_all_agents(self) -> List[BaseAgent]:
        return list(self._agents.values())

agent_registry = AgentRegistry()
