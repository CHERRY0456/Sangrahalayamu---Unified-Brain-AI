import logging
import json
from typing import AsyncGenerator
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.retrieval.models import ContextPackage
from app.services.prompts.prompt_engine import prompt_engine
from app.services.llm.llm_service import llm_service
from app.services.llm.schemas.generation_models import GenerationRequest
from app.services.validation.response_validator import response_validator, AIResponse
from app.services.validation.response_formatter import response_formatter
from app.services.conversation.conversation_manager import conversation_manager
from app.services.audit import audit_service, AuditEvent, EVENT_TYPE_AI_GENERATION
from app.services.agents.agent_orchestrator import agent_orchestrator, AgentContext

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """
    Central orchestration point for Generation.
    Takes a verified ContextPackage and User Identity, generates a prompt, manages history,
    calls the LLM provider, validates the response, and records metrics.
    """
    def __init__(self):
        pass

    async def generate(self, db: Session, query: str, context_package: ContextPackage, user: User, workspace_id: str, conversation_id: str) -> AIResponse:
        # 1. Retrieve history
        history = conversation_manager.get_conversation_history(db, conversation_id, user.id, workspace_id, limit=5)
        
        # 2. Run Autonomous Agents (Phase 4 integration)
        agent_context = AgentContext(query=query, workspace_id=workspace_id, user_id=user.id, parameters={})
        agent_results = await agent_orchestrator.execute_agents(agent_context)
        
        # 3. Build prompt
        system_prompt, user_prompt = prompt_engine.generate_prompt(query, context_package, history, agent_results)
        
        req = GenerationRequest(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.1,  # Low temp for grounded answers
            max_tokens=2048
        )
        
        # 3. Call LLM
        llm_response = llm_service.generate(req)
        
        # 4. Validate output
        validated = response_validator.validate_and_parse(llm_response.text)
        
        # 5. Format final response
        metadata = {
            "model": llm_response.model_id,
            "latency": llm_response.latency,
            "usage": llm_response.usage,
            "context_tokens": context_package.token_count
        }
        final_response = response_formatter.format_response(
            validated_response=validated,
            metadata=metadata,
            provenance=context_package.provenance
        )
        
        # 6. Save history
        conversation_manager.add_message(db, conversation_id, user.id, workspace_id, "user", query)
        # We store the raw JSON string of the AIResponse as content for the AI message
        ai_content = final_response.model_dump_json()
        conversation_manager.add_message(db, conversation_id, user.id, workspace_id, "ai", ai_content, metadata=metadata)
        
        # 7. Record Audit / Observability
        try:
            audit_service.record_event(db, AuditEvent(
                event_type=EVENT_TYPE_AI_GENERATION,
                actor_id=user.id,
                actor_role=user.role.name if user.role else "User",
                action="generate",
                status="SUCCESS",
                source_service="ai_orchestrator",
                metadata={"model": llm_response.model_id, "tokens_used": llm_response.usage.get("output_tokens", 0)}
            ))
        except Exception as e:
            logger.warning(f"Failed to record audit event for AI generation: {e}")

        return final_response

    async def stream_generate(self, db: Session, query: str, context_package: ContextPackage, user: User, workspace_id: str, conversation_id: str) -> AsyncGenerator[str, None]:
        """
        Streams answer tokens to the client. At the end, yields a final JSON block with citations and metadata.
        """
        history = conversation_manager.get_conversation_history(db, conversation_id, user.id, workspace_id, limit=5)
        
        # Run Autonomous Agents
        agent_context = AgentContext(query=query, workspace_id=workspace_id, user_id=user.id, parameters={})
        agent_results = await agent_orchestrator.execute_agents(agent_context)
        
        system_prompt, user_prompt = prompt_engine.generate_prompt(query, context_package, history, agent_results)
        
        req = GenerationRequest(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=2048
        )
        
        # We accumulate the text to parse it at the end to save history
        accumulated_text = ""
        final_metadata = None
        
        async for event in llm_service.stream_generate(req):
            if not event.is_final:
                accumulated_text += event.chunk
                yield event.chunk
            else:
                final_metadata = event.metadata
                
        # Validate and format once complete to ensure safety and structure
        try:
            validated = response_validator.validate_and_parse(accumulated_text)
            metadata = {
                "model": final_metadata.get("model", "unknown") if final_metadata else "unknown",
                "latency": final_metadata.get("latency", 0) if final_metadata else 0,
                "usage": final_metadata.get("usage", {}) if final_metadata else {},
                "context_tokens": context_package.token_count
            }
            final_response = response_formatter.format_response(
                validated_response=validated,
                metadata=metadata,
                provenance=context_package.provenance
            )
            
            # Emit final structured payload containing citations, confidence, etc.
            yield "\n__FINAL_PAYLOAD__\n"
            yield final_response.model_dump_json()

            # Save to history
            conversation_manager.add_message(db, conversation_id, user.id, workspace_id, "user", query)
            conversation_manager.add_message(db, conversation_id, user.id, workspace_id, "ai", final_response.model_dump_json(), metadata=metadata)
            
            # Audit
            try:
                audit_service.record_event(db, AuditEvent(
                    event_type=EVENT_TYPE_AI_GENERATION,
                    actor_id=user.id,
                    actor_role=user.role.name if user.role else "User",
                    action="stream_generate",
                    status="SUCCESS",
                    source_service="ai_orchestrator",
                    metadata={"model": metadata["model"]}
                ))
            except Exception as e:
                pass

        except Exception as e:
            logger.error(f"Validation failed after streaming: {e}")
            yield f"\n__ERROR__\nValidation failed: {e}"

ai_orchestrator = AIOrchestrator()
