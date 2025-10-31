"""Robust JSON parser for LLM outputs with graceful fallback."""

import json
import re
from typing import Dict, Any, Optional, List
import structlog
from pydantic import ValidationError

try:
    from json_repair import repair_json  # type: ignore[reportMissingImports]
    JSON_REPAIR_AVAILABLE = True
except ImportError:
    JSON_REPAIR_AVAILABLE = False
    repair_json = None

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
        - Malformed JSON with control characters
        """
        # Try direct JSON parse first
        try:
            parsed = json.loads(text)
            return parsed
        except json.JSONDecodeError as e:
            logger.debug(f"Direct JSON parse failed at position {e.pos}: {str(e.msg)}, trying alternatives...")
            pass

        # Try json-repair library if available (handles most malformed JSON)
        if JSON_REPAIR_AVAILABLE and repair_json:
            try:
                repaired = repair_json(text)
                parsed = json.loads(repaired)
                if isinstance(parsed, dict):
                    logger.info("Successfully repaired malformed JSON")
                    return parsed
            except Exception as e:
                logger.debug(f"JSON repair failed: {str(e)}")
                pass

        # Try to extract JSON from code blocks
        code_block_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        match = re.search(code_block_pattern, text, re.DOTALL)
        if match:
            json_str = match.group(1)
            # Try to fix common issues with newlines in strings
            json_str = RobustJSONParser._fix_control_chars(json_str)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.debug(f"Code block JSON parse failed: {str(e.msg)}")
                # Try json-repair on extracted code block
                if JSON_REPAIR_AVAILABLE and repair_json:
                    try:
                        repaired = repair_json(json_str)
                        return json.loads(repaired)
                    except Exception:
                        pass

        # Try to find JSON object in text - use a more robust approach
        # Find all potential JSON objects by balancing braces
        brace_stack = []
        start_idx = None
        candidates = []
        
        for i, char in enumerate(text):
            if char == '{':
                if not brace_stack:
                    start_idx = i
                brace_stack.append(char)
            elif char == '}':
                if brace_stack:
                    brace_stack.pop()
                    if not brace_stack and start_idx is not None:
                        # Found a complete JSON object - save it
                        candidates.append(text[start_idx:i+1])
                        start_idx = None
        
        # Try parsing all candidates, prefer the longest valid one (most complete)
        candidates.sort(key=len, reverse=True)
        for potential_json in candidates:
            # Fix control characters
            fixed_json = RobustJSONParser._fix_control_chars(potential_json)
            try:
                parsed = json.loads(fixed_json)
                if isinstance(parsed, dict) and len(parsed) > 0:
                    logger.debug(f"Successfully extracted JSON of length {len(potential_json)}")
                    return parsed
            except json.JSONDecodeError as e:
                logger.debug(f"JSON parse failed at pos {e.pos}: {e.msg}")
                # Try json-repair as last resort
                if JSON_REPAIR_AVAILABLE and repair_json:
                    try:
                        repaired = repair_json(potential_json)
                        parsed = json.loads(repaired)
                        if isinstance(parsed, dict) and len(parsed) > 0:
                            logger.info("Successfully repaired extracted JSON")
                            return parsed
                    except Exception:
                        pass
                continue

        return None

    @staticmethod
    def _fix_control_chars(json_str: str) -> str:
        """Fix common control character issues in JSON strings."""
        # Replace unescaped newlines within string values
        # This is a simple heuristic: find ": " followed by content with \n before closing "
        # More sophisticated: use regex to find string values and escape their content
        
        # Simple approach: replace literal \n in JSON strings with \\n
        # This won't work for all cases but handles the common issue
        result = json_str
        
        # Find all string values in JSON and escape newlines
        # Pattern: "key": "value with \n in it"
        pattern = r'":\s*"([^"]*)"'
        
        def escape_newlines(match):
            value = match.group(1)
            # Escape unescaped newlines and tabs
            value = value.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            return f'": "{value}"'
        
        result = re.sub(pattern, escape_newlines, result)
        return result

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

        logger.info("LLM response missing required 'answer' field, reconstructing from structured data")

        # Extract whatever we can
        data = RobustJSONParser.extract_json_from_text(text)
        if not data:
            # Log the problematic text for debugging
            logger.warning("Could not extract JSON from LLM output, attempting to use raw text", 
                          text_preview=text[:200] if text else "empty")
            
            # If the text looks like a plain text response (no JSON at all),
            # use it directly as the answer
            if text and len(text.strip()) > 50 and not text.strip().startswith('{'):
                return QAResponse(
                    executive_summary=[],
                    requirements_by_page={},
                    implementation_checklist=[],
                    pitfalls=[],
                    definitions={},
                    answer=text.strip(),
                    sources=[],
                    follow_up_questions=[],
                    confidence_score=0.6,
                )
            
            # Last resort: return minimal valid response
            logger.error("LLM returned invalid output - neither JSON nor usable text")
            return QAResponse(
                executive_summary=[
                    "Unable to parse structured response",
                    "Please try rephrasing your question",
                    "The system encountered a formatting error",
                ],
                requirements_by_page={},
                implementation_checklist=[
                    "Review the question for clarity",
                    "Ensure the query relates to AAOIFI standards",
                    "Try a more specific question",
                ],
                pitfalls=["Response parsing failed", "Unable to extract structured information"],
                definitions={},
                answer="I encountered a formatting error while processing your question. Please try rephrasing your question or asking about a specific aspect of the AAOIFI Sharia Standards.",
                sources=[],
                follow_up_questions=[
                    "Could you rephrase your question?",
                    "What specific aspect are you interested in?",
                ],
                confidence_score=0.1,
            )

        # Build partial response with defaults
        # Extract answer field - if missing, try to construct from other fields
        answer_text = data.get("answer", "")
        if not answer_text or len(str(answer_text).strip()) < 50:
            # Construct answer from available structured data
            answer_parts = []
            if data.get("executive_summary"):
                answer_parts.append("**Key Points:**")
                for point in data.get("executive_summary", []):
                    answer_parts.append(f"- {point}")
            if data.get("requirements_by_page"):
                answer_parts.append("\n**Requirements:**")
                for page, reqs in data.get("requirements_by_page", {}).items():
                    if isinstance(reqs, list):
                        for req in reqs:
                            answer_parts.append(f"- {req} (Page {page})")
            if data.get("implementation_checklist"):
                answer_parts.append("\n**Implementation Steps:**")
                for i, step in enumerate(data.get("implementation_checklist", []), 1):
                    answer_parts.append(f"{i}. {step}")
            
            if answer_parts:
                answer_text = "\n".join(answer_parts)
            else:
                answer_text = (
                    "I found relevant information in the standards, but the response structure "
                    "was incomplete. Please try rephrasing your question for better results."
                )
        
        partial = {
            "executive_summary": RobustJSONParser._extract_list(
                data.get("executive_summary", []),
                min_items=3,
                default=[
                    "Information extracted from standards",
                    "Partial response available",
                    "See details below",
                ],
            ),
            "requirements_by_page": RobustJSONParser._extract_dict(
                data.get("requirements_by_page", {}), default={}
            ),
            "implementation_checklist": RobustJSONParser._extract_list(
                data.get("implementation_checklist", []),
                min_items=3,
                default=[
                    "Review extracted information",
                    "Verify with original standards",
                    "Consult with Sharia expert",
                ],
            ),
            "pitfalls": RobustJSONParser._extract_list(
                data.get("pitfalls", []),
                min_items=2,
                default=["Response may be incomplete", "Verify critical details"],
            ),
            "definitions": RobustJSONParser._extract_dict(data.get("definitions", {}), default={}),
            "answer": answer_text,  # CRITICAL: Include the answer field
            "sources": RobustJSONParser._extract_list(
                data.get("sources", []), min_items=0, default=[]
            ),
            "follow_up_questions": RobustJSONParser._extract_list(
                data.get("follow_up_questions", []),
                min_items=2,
                default=["What specific details do you need?", "Which aspect should I clarify?"],
            ),
            "confidence_score": float(data.get("confidence_score", 0.5)),
        }

        try:
            return QAResponse(**partial)
        except ValidationError as e:
            logger.error("Even partial response failed validation", errors=str(e))
            # Return absolute minimum valid response
            return QAResponse(
                executive_summary=[
                    "Response parsing failed",
                    "Partial data unavailable",
                    "Please try again",
                ],
                requirements_by_page={},
                implementation_checklist=[
                    "Retry the query",
                    "Simplify the question",
                    "Contact support",
                ],
                pitfalls=["Data extraction failed", "System error occurred"],
                definitions={},
                answer="I encountered an error while processing your question. The response data could not be properly formatted. Please try asking your question in a different way, or contact support if the issue persists.",
                sources=[],
                follow_up_questions=[
                    "Can you try a different question?",
                    "What information do you need?",
                ],
                confidence_score=0.0,
            )

    @staticmethod
    def _extract_list(value: Any, min_items: int, default: List[str]) -> List[str]:
        """Extract and validate list from value."""
        if not isinstance(value, list):
            return default

        valid_items = [str(item) for item in value if item]

        if len(valid_items) < min_items:
            valid_items.extend(default[len(valid_items) : min_items])

        return valid_items[: max(len(valid_items), min_items)]

    @staticmethod
    def _extract_dict(value: Any, default: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and validate dict from value."""
        if not isinstance(value, dict):
            return default
        return {str(k): v for k, v in value.items() if k and v}


# Singleton instance
robust_parser = RobustJSONParser()
