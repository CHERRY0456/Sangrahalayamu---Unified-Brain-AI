import time
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import uuid

from app.models.user import User
from app.services.retrieval import hybrid_retrieval_service, RetrievalFilters
from .models import AIResponse, GenerationMetadata
from .context import ConversationalContextResolver
from app.services.ai.ai_orchestrator import ai_orchestrator

logger = logging.getLogger("sangrahalayamu.orchestrator.service")

class AIOrchestratorService:
    """
    Thin compatibility layer. 
    Delegates all generation and RAG logic to Phase 3 ai_orchestrator, preserving existing endpoints.
    """
    def __init__(self):
        pass

    def generate_response(
        self,
        db: Session,
        query: str,
        user: User,
        conversation_context: Optional[List[Dict[str, str]]] = None,
        retrieval_filters: Optional[RetrievalFilters] = None,
        prompt_template: str = "enterprise_default"
    ) -> AIResponse:
        
        # 1. Pronoun context resolution (kept for backward compatibility)
        history = conversation_context or []
        resolved_query = ConversationalContextResolver.resolve_pronouns(query, history)
        
        # 2. Hybrid Retrieval Execution (returns ContextPackage in Phase 2)
        context_package = hybrid_retrieval_service.retrieve(
            db=db,
            query=resolved_query,
            user=user,
            filters=retrieval_filters,
            limit=4
        )
        
        # Generate fallback IDs for the new conversation manager since legacy endpoints didn't provide them
        workspace_id = "default-workspace"
        conversation_id = str(uuid.uuid4())
        
        # 3. Delegate to Phase 3 Orchestrator
        new_response = ai_orchestrator.generate(
            db=db,
            query=resolved_query,
            context_package=context_package,
            user=user,
            workspace_id=workspace_id,
            conversation_id=conversation_id
        )

        # 4. Map back to legacy schema (AIResponse from .models)
        gen_meta = GenerationMetadata(
            provider="Phase3-AI-Orchestrator",
            model=new_response.metadata.get("model", "unknown") if new_response.metadata else "unknown",
            prompt_template=prompt_template,
            retrieval_context_size=context_package.token_count,
            validation_attempts=1,
            orchestrator_version="3.0.0"
        )
        
        temp_res = AIResponse(
            answer=new_response.answer,
            citations=new_response.citations,
            confidence=new_response.confidence,
            retrieval_summary={"context_tokens": context_package.token_count},
            sources=new_response.provenance or [],
            warnings=new_response.warnings,
            token_usage=new_response.metadata.get("usage", {}) if new_response.metadata else {},
            latency={"total": new_response.metadata.get("latency", 0) if new_response.metadata else 0},
            generation_metadata=gen_meta
        )

        # Transparency Engine
        from app.core.config import settings
        transparency_report = None
        if settings.flags.enable_transparency:
            from app.services.transparency import transparency_engine
            transparency_report = transparency_engine.generate_explanation(
                db=db,
                ai_response=temp_res,
                retrieval_package=context_package, # Might need to adapt a bit if it strictly expects HybridRetrievalPackage
                user=user
            )

        temp_res.transparency_report = transparency_report

        return temp_res

# Expose global singleton instance for service routing pings
ai_orchestrator_service = AIOrchestratorService()
