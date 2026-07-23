from typing import List, Dict, Any, Tuple
from app.services.retrieval.models import ContextPackage
from .prompt_builder import PromptBuilder

class PromptEngine:
    """
    Central engine for generating prompt components for the AI Orchestrator.
    """
    def generate_prompt(
        self, 
        query: str, 
        context_package: ContextPackage, 
        history: List[Dict[str, str]] = None,
        agent_results: List[Any] = None
    ) -> Tuple[str, str]:
        """
        Assembles and returns the (system_prompt, user_prompt) tuple.
        """
        builder = PromptBuilder(query)
        builder.with_context(context_package)
        builder.with_history(history or [])
        if agent_results:
            builder.with_agent_evidence(agent_results)
        return builder.build()

prompt_engine = PromptEngine()
