"""Chat API endpoints."""
from fastapi import APIRouter, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from app.schemas.chat import ChatRequest, ChatResponse, SourceDocument
from app.core.rag_engine_pro import rag_engine_pro as rag_engine
from app.services.conversation_service import conversation_service
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Handle chat requests with RAG."""
    try:
        logger.info("Processing chat request", message_length=len(request.message), 
                   conversation_id=request.conversation_id)
        
        # If conversation_id is provided, save the user message
        if request.conversation_id:
            try:
                conversation_service.add_message(
                    conversation_id=request.conversation_id,
                    role="user",
                    content=request.message,
                    sources=None
                )
            except Exception as e:
                logger.warning("Failed to save user message", error=str(e))
        
        answer, sources, follow_up_questions = rag_engine.answer_question(
            request.message, 
            tone=request.tone.value if request.tone else "conversational"
        )
        
        source_docs = []
        for i, doc in enumerate(sources):
            metadata = doc.metadata or {}
            page = metadata.get("page", 0)
            source_file = metadata.get("source", metadata.get("file_path", "AAOIFI Standards"))
            relevance_score = metadata.get("relevance_score", 0.0)
            
            # Extract content with context
            content = doc.page_content
            excerpt_length = 200
            
            # Get excerpt and context
            if len(content) > excerpt_length:
                excerpt = content[:excerpt_length] + "..."
                context_after = content[excerpt_length:excerpt_length+100] if len(content) > excerpt_length else None
            else:
                excerpt = content
                context_after = None
            
            source_docs.append(SourceDocument(
                page=int(page) if isinstance(page, (int, float, str)) and str(page).replace('.','').isdigit() else 0,
                content=excerpt,
                score=float(relevance_score) if relevance_score else 0.0,
                chunk_id=metadata.get("id", metadata.get("chunk_id", f"chunk_{i}")),
                source_file=str(source_file) if source_file else None,
                start_char=metadata.get("start_char"),
                end_char=metadata.get("end_char"),
                context_before=None,  # TODO: Could extract from previous chunk
                context_after=context_after,
                metadata={
                    "full_content_length": len(content),
                    "retrieval_position": i + 1,
                    "has_full_content": len(content) <= excerpt_length
                }
            ))
        
        # If conversation_id is provided, save the assistant response
        if request.conversation_id:
            try:
                conversation_service.add_message(
                    conversation_id=request.conversation_id,
                    role="assistant",
                    content=answer,
                    sources=[{"page": doc.page, "content": doc.content, "score": doc.score} 
                            for doc in source_docs]
                )
            except Exception as e:
                logger.warning("Failed to save assistant message", error=str(e))
        
        logger.info("Chat successful", answer_length=len(answer), sources_count=len(source_docs))
        
        return ChatResponse(
            answer=answer,
            sources=source_docs,
            follow_up_questions=follow_up_questions if follow_up_questions else None,
            metadata={"sources_count": len(source_docs), "conversation_id": request.conversation_id}
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error("Chat error", error=str(e), traceback=error_trace)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.post("/clear")
async def clear_conversation():
    """Clear conversation history."""
    rag_engine.clear_memory()
    return {"message": "Conversation cleared"}
