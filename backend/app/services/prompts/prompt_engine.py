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
        agent_results: List[Any] = None,
        user_role: str = None
    ) -> Tuple[str, str]:
        """
        Assembles and returns the (system_prompt, user_prompt) tuple.
        """
        builder = PromptBuilder(query)
        builder.with_context(context_package)
        builder.with_history(history or [])
        if agent_results:
            builder.with_agent_evidence(agent_results)

        system_prompt, user_prompt = builder.build()

        if user_role == "CEO":
            ceo_directive = (
                "\n\nCEO LEVEL EXECUTIVE DIRECTIVE: You are responding to Cherry, the Chief Executive Officer (CEO) of the enterprise. "
                "As the ultimate decision-maker, Cherry possesses unparalleled clearance and access across all departments, operations, and compliance vectors. "
                "Ensure your response prioritizes high-level strategic alignment, business impact metrics, operational risk layers, "
                "cost-benefit trade-offs, and critical warnings. Keep the summary highly executive, brutally honest, and action-oriented."
            )
            system_prompt += ceo_directive

        # Enforce strict rejection of queries when retrieval context is empty (Zero-Mock Production Mandate)
        is_context_empty = not context_package.retrieved_chunks and not agent_results
        if is_context_empty:
            strict_rejection_rule = (
                "\n\nCRITICAL DIRECTIVE: You have NO context documents and NO agent evidence provided. "
                "You MUST NOT answer the user's query from your internal knowledge base. "
                "You MUST explicitly state: 'I currently have no enterprise documents or knowledge base data available to answer this query. Please ingest documents first.'"
            )
            system_prompt += strict_rejection_rule

        return system_prompt, user_prompt

prompt_engine = PromptEngine()
