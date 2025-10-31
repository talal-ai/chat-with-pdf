"""Conversation management API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from app.services.conversation_service import conversation_service
import structlog

logger = structlog.get_logger()
router = APIRouter()


class CreateConversationRequest(BaseModel):
    """Request model for creating a conversation."""

    title: str = Field(..., min_length=1, max_length=200, description="Conversation title")
    metadata: Optional[dict] = Field(default=None, description="Optional metadata")


class CreateConversationResponse(BaseModel):
    """Response model for creating a conversation."""

    conversation_id: int
    title: str
    created_at: str


class ConversationSummary(BaseModel):
    """Summary of a conversation."""

    id: int
    title: str
    created_at: str
    updated_at: str
    message_count: int
    metadata: dict


class Message(BaseModel):
    """Message model."""

    id: int
    role: str
    content: str
    sources: List[dict]
    timestamp: str


class ConversationDetail(BaseModel):
    """Detailed conversation with messages."""

    id: int
    title: str
    created_at: str
    updated_at: str
    message_count: int
    metadata: dict
    messages: List[Message]


class UpdateTitleRequest(BaseModel):
    """Request to update conversation title."""

    title: str = Field(..., min_length=1, max_length=200)


@router.post("/conversations", response_model=CreateConversationResponse)
async def create_conversation(request: CreateConversationRequest):
    """Create a new conversation."""
    try:
        conversation_id = conversation_service.create_conversation(
            title=request.title, metadata=request.metadata
        )

        # Get the created conversation to return full details
        conversation = conversation_service.get_conversation(conversation_id)

        return CreateConversationResponse(
            conversation_id=conversation_id,
            title=conversation["title"],
            created_at=conversation["created_at"],
        )
    except Exception as e:
        logger.error("Failed to create conversation", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")


@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of conversations to return"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip"),
):
    """List all conversations ordered by most recent."""
    try:
        conversations = conversation_service.list_conversations(limit=limit, offset=offset)
        return [ConversationSummary(**conv) for conv in conversations]
    except Exception as e:
        logger.error("Failed to list conversations", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list conversations: {str(e)}")


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: int):
    """Get a specific conversation with all messages."""
    try:
        conversation = conversation_service.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")

        return ConversationDetail(**conversation)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get conversation", error=str(e), conversation_id=conversation_id)
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")


@router.patch("/conversations/{conversation_id}/title")
async def update_conversation_title(conversation_id: int, request: UpdateTitleRequest):
    """Update the title of a conversation."""
    try:
        updated = conversation_service.update_conversation_title(conversation_id, request.title)

        if not updated:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")

        return {"message": "Title updated successfully", "conversation_id": conversation_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update title", error=str(e), conversation_id=conversation_id)
        raise HTTPException(status_code=500, detail=f"Failed to update title: {str(e)}")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: int):
    """Delete a conversation and all its messages."""
    try:
        deleted = conversation_service.delete_conversation(conversation_id)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")

        return {"message": "Conversation deleted successfully", "conversation_id": conversation_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete conversation", error=str(e), conversation_id=conversation_id)
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")
