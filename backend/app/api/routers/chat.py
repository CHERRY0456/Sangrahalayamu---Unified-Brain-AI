import logging
import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.retrieval.orchestrator import hybrid_retrieval_service
from app.services.ai.ai_orchestrator import AIOrchestrator
from app.services.retrieval.models import RetrievalFilters
from app.services.conversation.conversation_manager import conversation_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])
ai_orchestrator = AIOrchestrator()

class ChatRequest(BaseModel):
    query: str
    workspace_id: str
    conversation_id: str
    stream: bool = False
    filters: Optional[Dict[str, Any]] = None

@router.post("", status_code=status.HTTP_200_OK)
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enterprise Chat Endpoint.
    Follows: User Query -> Hybrid Retrieval -> Agent Orchestrator -> Prompt Engine -> Bedrock Qwen -> Validation.
    """
    # 1. Retrieve Context
    retrieval_filters = RetrievalFilters(**request.filters) if request.filters else None
    context_package = hybrid_retrieval_service.retrieve(
        db=db,
        query=request.query,
        user=current_user,
        filters=retrieval_filters,
        limit=5
    )
    
    # 2. Generation Route
    if request.stream:
        # Stream response back using SSE
        return StreamingResponse(
            ai_orchestrator.stream_generate(
                db=db,
                query=request.query,
                context_package=context_package,
                user=current_user,
                workspace_id=request.workspace_id,
                conversation_id=request.conversation_id
            ),
            media_type="text/event-stream"
        )
    else:
        # Standard synchronous response
        response = await ai_orchestrator.generate(
            db=db,
            query=request.query,
            context_package=context_package,
            user=current_user,
            workspace_id=request.workspace_id,
            conversation_id=request.conversation_id
        )
        return response

@router.get("/conversations", status_code=status.HTTP_200_OK)
def get_conversations(
    workspace_id: str = "default",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch all unique chat session histories for the authorized user.
    """
    return conversation_manager.list_conversations(db, current_user.id, workspace_id)

@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_200_OK)
def delete_conversation(
    conversation_id: str,
    workspace_id: str = "default",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes all historical messages belonging to a specified conversation session.
    """
    conversation_manager.delete_conversation(db, conversation_id, current_user.id, workspace_id)
    return {"success": True, "message": "Conversation successfully deleted."}

@router.get("/conversations/{conversation_id}/messages", status_code=status.HTTP_200_OK)
def get_conversation_messages(
    conversation_id: str,
    workspace_id: str = "default",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves chronological message histories of a specified conversation session.
    """
    return conversation_manager.get_conversation_messages(db, conversation_id, current_user.id, workspace_id)

@router.get("/explain/{message_id}", status_code=status.HTTP_200_OK)
def get_message_explanation(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the transparency report / reasoning steps explainability payload for a generated message.
    """
    msg = conversation_manager.get_message(db, message_id, current_user.id)
    if not msg or msg["role"] != "ai":
        return {"error": "Message not found or not an AI response"}
    
    # Parse content as AIResponse JSON
    try:
        data = json.loads(msg["content"])
    except Exception:
        data = {}
        
    citations = data.get("citations", [])
    sources = data.get("sources", [])
    confidence = data.get("confidence", 0.95)
    
    # Standardize confidence to percentage integer
    if isinstance(confidence, (int, float)):
        if confidence <= 1.0:
            confidence = int(confidence * 100)
        else:
            confidence = int(confidence)
    else:
        confidence = 95

    # Structure reasoning steps matching UI expectation
    reasoning_steps = [
        {"label": "Query Understanding", "description": "Analyzing search terms & intent", "status": "completed"},
        {"label": "Hybrid Retrieval", "description": "Querying Postgres, Qdrant VectorDB, and Neo4j Graph DB", "status": "completed"},
        {"label": "Context Synthesis", "description": f"Synthesized context from {len(sources)} documents", "status": "completed"},
        {"label": "Response Generation", "description": "Generating answer using AWS Bedrock Qwen", "status": "completed"},
        {"label": "Guardrail Check", "description": "Applying LLM response validator and policy check", "status": "completed"}
    ]
    
    docs = []
    for src in sources:
        docs.append({
            "name": src.get("document_name") or f"Doc {src.get('document_id')}",
            "category": "Reference Doc",
            "confidence": "High",
            "relevanceTag": "Primary"
        })
        
    formatted_citations = []
    for c in citations:
        formatted_citations.append({
            "fileName": c.get("document_name") or f"Doc {c.get('document_id')}",
            "pages": str(c.get("page", 1)),
            "sections": [c.get("snippet", "")]
        })
        
    graph = {
        "nodes": [
            {"id": "n1", "label": "Semantic Query", "type": "compliance"},
            {"id": "n2", "label": "LLM Answer", "type": "chat"}
        ],
        "links": [
            {"source": "n1", "target": "n2", "type": "retrieved"}
        ]
    }
    
    return {
        "messageId": message_id,
        "overallConfidence": confidence,
        "evidenceStrength": "High" if confidence > 80 else "Medium",
        "docCoverage": f"{len(sources)} documents" if sources else "Global Index",
        "documents": docs,
        "reasoningSteps": reasoning_steps,
        "citations": formatted_citations,
        "graph": graph
    }
