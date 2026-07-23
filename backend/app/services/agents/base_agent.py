from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel

class AgentContext(BaseModel):
    """
    Context passed to an agent to execute its task.
    """
    query: str
    workspace_id: str
    user_id: int
    parameters: Dict[str, Any] = {}

class AgentResult(BaseModel):
    """
    Structured result returned by an agent.
    """
    agent_name: str
    success: bool
    data: Dict[str, Any]
    confidence: float
    reasoning_summary: str

class BaseAgent(ABC):
    """
    Abstract interface for all specialized enterprise agents.
    Agents are stateless and independently testable.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the unique name of the agent."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Returns a description of what the agent does for routing purposes."""
        pass

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Executes the agent's core logic.
        """
        pass
