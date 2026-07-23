import json
from typing import List, Dict, Any
from app.services.retrieval.models import ContextPackage

from .prompt_templates import SYSTEM_IDENTITY, RESPONSE_SCHEMA_INSTRUCTIONS, STEP_BACK_INSTRUCTIONS
from .decision_rubrics import DECISION_RUBRIC, REASONING_INSTRUCTIONS
from .guardrails import GUARDRAILS

class PromptBuilder:
    """
    Builder pattern for constructing dynamic, highly structured LLM prompts.
    """
    def __init__(self, query: str):
        self.query = query
        self.system = SYSTEM_IDENTITY
        self.step_back = STEP_BACK_INSTRUCTIONS
        self.context = ""
        self.rubric = DECISION_RUBRIC
        self.reasoning = REASONING_INSTRUCTIONS
        self.guardrails = GUARDRAILS
        self.schema = RESPONSE_SCHEMA_INSTRUCTIONS
        self.history = ""
        
    def with_context(self, context_package: ContextPackage):
        """Injects the retrieved context package as JSON strings for the LLM."""
        chunks_str = ""
        for idx, chunk in enumerate(context_package.retrieved_chunks):
            chunks_str += f"[Citation ID: {chunk.chunk_id}]\n"
            chunks_str += f"Source: {chunk.document_name} (Section: {chunk.section})\n"
            chunks_str += f"Text: {chunk.text}\n\n"
            
        self.context = f"<retrieved_context>\n{chunks_str}</retrieved_context>"
        return self
        
    def with_history(self, history: List[Dict[str, str]]):
        """Injects conversation history."""
        if not history:
            return self
            
        hist_str = ""
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            hist_str += f"{role.upper()}: {content}\n"
            
        self.history = f"<conversation_history>\n{hist_str}</conversation_history>"
        return self

    def with_agent_evidence(self, agent_results: List[Any]):
        """Injects structured evidence from Specialized AI Agents (Graph Reasoning)."""
        if not agent_results:
            return self
            
        evidence_str = ""
        for res in agent_results:
            evidence_str += f"[Agent: {res.agent_name} | Confidence: {res.confidence}]\n"
            evidence_str += f"Summary: {res.reasoning_summary}\n"
            evidence_str += f"Data: {json.dumps(res.data, indent=2)}\n\n"
            
        self.agent_evidence = f"<agent_evidence>\n{evidence_str}</agent_evidence>"
        return self

    def build(self) -> tuple[str, str]:
        """
        Returns (system_prompt, user_prompt)
        """
        agent_evidence_block = getattr(self, "agent_evidence", "")
        
        user_prompt = f"""{self.step_back}

{self.context}

{agent_evidence_block}

{self.history}

{self.rubric}

{self.reasoning}

{self.guardrails}

{self.schema}

USER QUERY:
{self.query}"""
        return self.system, user_prompt
