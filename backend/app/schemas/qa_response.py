"""Flexible response schema for natural, context-aware answers."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional


class QAResponse(BaseModel):
    """Flexible response schema that adapts to question type."""

    executive_summary: List[str] = Field(
        default_factory=list,
        description="Optional: 2-5 key points for complex topics. Leave empty for simple questions.",
    )

    requirements_by_page: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Optional: Requirements grouped by page when relevant. Can be empty for non-requirement questions.",
    )

    implementation_checklist: List[str] = Field(
        default_factory=list,
        description="Optional: Action steps for 'how-to' questions. Leave empty if not applicable.",
    )

    pitfalls: List[str] = Field(
        default_factory=list,
        description="Optional: Warnings and edge cases when relevant. Can be empty.",
    )

    definitions: Dict[str, str] = Field(
        default_factory=dict, description="Optional: Key terms that need explanation. Can be empty."
    )

    answer: str = Field(
        ...,
        min_length=50,
        description="REQUIRED: Natural, conversational answer that directly addresses the question. Can be short or long based on question complexity.",
    )

    sources: List[str] = Field(
        default_factory=list, description="Page numbers referenced in the answer"
    )

    follow_up_questions: List[str] = Field(
        default_factory=list,
        max_length=4,
        description="Optional: 2-4 relevant follow-up questions when they add value",
    )

    confidence_score: Optional[float] = Field(
        default=0.8, ge=0.0, le=1.0, description="Confidence in the response quality (0.0-1.0)"
    )

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, v):
        """Ensure answer is meaningful."""
        if not v or not v.strip():
            raise ValueError("Answer must not be empty")
        return v


class MultiQueryResponse(BaseModel):
    """Response for multi-query expansion."""

    queries: List[str] = Field(..., min_length=3, max_length=5)
