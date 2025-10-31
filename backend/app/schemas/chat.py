"""Pydantic schemas for chat API."""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ResponseTone(str, Enum):
    """Response tone options for flexible AI responses."""

    CONVERSATIONAL = "conversational"  # Like ChatGPT - friendly, natural
    CONCISE = "concise"  # Short, to-the-point answers
    DETAILED = "detailed"  # Comprehensive explanations
    PROFESSIONAL = "professional"  # Formal consultant style
    SIMPLE = "simple"  # Explain like I'm 5


class SourceDocument(BaseModel):
    """Source document with detailed metadata."""

    page: int = Field(..., description="Page number in the source document")
    content: str = Field(..., description="Excerpt from the source")
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="Relevance score (0-1)")
    chunk_id: Optional[str] = Field(default=None, description="Unique chunk identifier")
    source_file: Optional[str] = Field(default=None, description="Source document filename")
    start_char: Optional[int] = Field(default=None, description="Character start position in page")
    end_char: Optional[int] = Field(default=None, description="Character end position in page")
    context_before: Optional[str] = Field(default=None, description="Text before the excerpt")
    context_after: Optional[str] = Field(default=None, description="Text after the excerpt")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str = Field(..., min_length=1, max_length=2000, description="User's question")
    conversation_history: Optional[List[dict]] = Field(default=[], description="Previous messages")
    conversation_id: Optional[int] = Field(
        default=None, description="Optional conversation ID to save messages"
    )
    tone: Optional[ResponseTone] = Field(
        default=ResponseTone.CONVERSATIONAL, description="Response tone/style"
    )


class ChatResponse(BaseModel):
    """Chat response model with sources."""

    answer: str = Field(..., description="AI-generated answer")
    sources: List[SourceDocument] = Field(
        default_factory=list, description="Source documents with page references"
    )
    follow_up_questions: Optional[List[str]] = Field(
        default=None, description="Suggested follow-up questions"
    )
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str = "1.0.0"
