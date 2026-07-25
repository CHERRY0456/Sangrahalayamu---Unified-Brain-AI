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

        # Determine if query is a general conversational phrase or greeting
        conversational_phrases = {
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "who are you", "what can you do", "help", "thanks", "thank you", "bye", "goodbye",
            "how are you", "what is your name"
        }
        clean_q = query.strip().lower().rstrip("!?.")
        is_greeting = clean_q in conversational_phrases or (len(clean_q.split()) <= 2 and not any(
            kw in clean_q for kw in ["valve", "pressure", "manual", "spec", "drawing", "p&id", "report", "csv", "log", "pump", "doc", "document", "file", "error", "fail"]
        ))

        is_context_empty = not context_package.retrieved_chunks and not agent_results

        if is_greeting:
            greeting_rule = (
                "\n\nCONVERSATIONAL DIRECTIVE: The user is greeting you or starting a casual conversation. "
                "Respond warmly, politely, and concisely as IndustryBrain-AI, the Enterprise Knowledge Intelligence Assistant. "
                "Briefly mention how you can assist with retrieving operational manuals, engineering specs, P&ID drawings, and audit logs."
            )
            system_prompt += greeting_rule
        elif is_context_empty:
            strict_rejection_rule = (
                "\n\nRETRIEVAL DIRECTIVE: No relevant document chunks were found in the knowledge repository matching this query. "
                "State clearly: 'No relevant document chunks or knowledge base data matching this query were found in the repository. Please upload the relevant document or refine your search.'"
            )
            system_prompt += strict_rejection_rule

        return system_prompt, user_prompt

prompt_engine = PromptEngine()
