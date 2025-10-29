"""Robust JSON parser for LLM outputs with graceful fallback."""
import json
import re
from typing import Dict, Any, Optional, List
import structlog
from pydantic import ValidationError

from app.schemas.qa_response import QAResponse

logger = structlog.get_logger()


class RobustJSONParser:
    """Parser that can extract partial structured data from malformed LLM outputs."""
    
    @staticmethod
    def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from text that may contain markdown code blocks or extra text.
        
        Handles cases like:
        - ```json\n{...}\n```
        - Here is the answer:\n{...}
        - {...} with trailing text
        """
        # Try direct JSON parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from code blocks
        code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(code_block_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON object in text
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        for potential_json in matches:
            try:
                parsed = json.loads(potential_json)
                if isinstance(parsed, dict) and len(parsed) > 0:
                    return parsed
            except json.JSONDecodeError:
                continue
        
        return None
    
    @staticmethod
    def parse_to_qa_response(text: str) -> Optional[QAResponse]:
        """
        Parse LLM output to QAResponse with validation.
        Returns None if parsing fails completely.
        """
        try:
            # Extract JSON
            data = RobustJSONParser.extract_json_from_text(text)
            if not data:
                logger.warning("Could not extract JSON from LLM output")
                return None
            
            # Try to create QAResponse with validation
            return QAResponse(**data)
            
        except ValidationError as e:
            logger.warning("QAResponse validation failed", errors=str(e))
            return None
        except Exception as e:
            logger.error("Unexpected error parsing QAResponse", error=str(e))
            return None
    
    @staticmethod
    def parse_with_fallback(text: str) -> QAResponse:
        """
        Parse LLM output with best-effort partial extraction.
        Always returns a valid QAResponse, even if partially filled.
        """
        # Try full parse first
        response = RobustJSONParser.parse_to_qa_response(text)
        if response:
            return response
        
        logger.info("Full parse failed, attempting partial extraction")
        
        # Extract whatever we can
        data = RobustJSONParser.extract_json_from_text(text)
        if not data:
            # Last resort: return minimal valid response
            return QAResponse(
                executive_summary=[
                    "Unable to parse structured response",
                    "Please try rephrasing your question",
                    "The system encountered a formatting error"
                ],
                requirements_by_page={},
                implementation_checklist=[
                    "Review the question for clarity",
                    "Ensure the query relates to AAOIFI standards",
                    "Try a more specific question"
                ],
                pitfalls=[
                    "Response parsing failed",
                    "Unable to extract structured information"
                ],
                definitions={},
                sources=[],
                follow_up_questions=[
                    "Could you rephrase your question?",
                    "What specific aspect are you interested in?"
                ],
                confidence_score=0.1
            )
        
        # Build partial response with defaults
        partial = {
            "executive_summary": RobustJSONParser._extract_list(
                data.get("executive_summary", []),
                min_items=3,
                default=["Information extracted from standards", "Partial response available", "See details below"]
            ),
            "requirements_by_page": RobustJSONParser._extract_dict(
                data.get("requirements_by_page", {}),
                default={}
            ),
            "implementation_checklist": RobustJSONParser._extract_list(
                data.get("implementation_checklist", []),
                min_items=3,
                default=["Review extracted information", "Verify with original standards", "Consult with Sharia expert"]
            ),
            "pitfalls": RobustJSONParser._extract_list(
                data.get("pitfalls", []),
                min_items=2,
                default=["Response may be incomplete", "Verify critical details"]
            ),
            "definitions": RobustJSONParser._extract_dict(
                data.get("definitions", {}),
                default={}
            ),
            "sources": RobustJSONParser._extract_list(
                data.get("sources", []),
                min_items=0,
                default=[]
            ),
            "follow_up_questions": RobustJSONParser._extract_list(
                data.get("follow_up_questions", []),
                min_items=2,
                default=["What specific details do you need?", "Which aspect should I clarify?"]
            ),
            "confidence_score": float(data.get("confidence_score", 0.5))
        }
        
        try:
            return QAResponse(**partial)
        except ValidationError as e:
            logger.error("Even partial response failed validation", errors=str(e))
            # Return absolute minimum valid response
            return QAResponse(
                executive_summary=["Response parsing failed", "Partial data unavailable", "Please try again"],
                requirements_by_page={},
                implementation_checklist=["Retry the query", "Simplify the question", "Contact support"],
                pitfalls=["Data extraction failed", "System error occurred"],
                definitions={},
                sources=[],
                follow_up_questions=["Can you try a different question?", "What information do you need?"],
                confidence_score=0.0
            )
    
    @staticmethod
    def _extract_list(value: Any, min_items: int, default: List[str]) -> List[str]:
        """Extract and validate list from value."""
        if not isinstance(value, list):
            return default
        
        valid_items = [str(item) for item in value if item]
        
        if len(valid_items) < min_items:
            valid_items.extend(default[len(valid_items):min_items])
        
        return valid_items[:max(len(valid_items), min_items)]
    
    @staticmethod
    def _extract_dict(value: Any, default: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and validate dict from value."""
        if not isinstance(value, dict):
            return default
        return {str(k): v for k, v in value.items() if k and v}


# Singleton instance
robust_parser = RobustJSONParser()
