"""LLM service using Groq for fast inference."""
from langchain_groq import ChatGroq
from app.core.config import settings
import structlog
from typing import Optional

logger = structlog.get_logger()


class LLMService:
    """Service for LLM interactions using Groq with lazy initialization."""
    
    def __init__(self):
        """Initialize service without creating LLM client yet."""
        self._llm: Optional[ChatGroq] = None
        self._initialized = False
        self._initialization_error: Optional[str] = None
        
        self.system_prompt = """You are a senior consultant specializing in AAOIFI Sharia Standards. Provide specific, detailed, and professionally structured responses. Extract and cite actual principles, requirements, and guidelines from the standards. Use precise terminology and cite page numbers as [Page X] for each distinct point."""
    
    def _initialize_llm(self):
        """Lazily initialize the Groq chat model on first access."""
        if self._initialized:
            return
        
        self._initialized = True
        
        # Validate API key first
        if not settings.groq_api_key:
            self._initialization_error = "GROQ_API_KEY is not set. Please configure it in your .env file."
            logger.error(self._initialization_error)
            return
        
        # List of fallback models in order of preference (fastest first)
        fallback_models = [
            "llama-3.1-8b-instant",  # Fastest for quick responses
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768",
            "llama-3.2-90b-text-preview"
        ]
        
        for model_name in [settings.groq_model] + fallback_models:
            try:
                self._llm = ChatGroq(
                    model=model_name,
                    temperature=settings.groq_temperature,
                    api_key=settings.groq_api_key,
                    max_tokens=2048,  # Limit response length for faster generation
                    timeout=30,  # 30 second timeout
                )
                logger.info("LLMService initialized successfully", model=model_name)
                return
            except Exception as e:
                logger.warning(f"Failed to initialize model {model_name}: {e}")
                continue
        
        self._initialization_error = "Failed to initialize any Groq model. Check your GROQ_API_KEY and network connection."
        logger.error(self._initialization_error)
    
    def get_llm(self):
        """Get the LLM instance, initializing it if necessary."""
        if not self._initialized:
            self._initialize_llm()
        
        if self._llm is None:
            error_msg = self._initialization_error or "LLM not initialized"
            raise RuntimeError(f"LLM unavailable: {error_msg}")
        
        return self._llm
    
    def get_system_prompt(self):
        """Get the system prompt."""
        return self.system_prompt
    
    def is_available(self) -> bool:
        """Check if LLM service is available without raising exceptions."""
        if not self._initialized:
            self._initialize_llm()
        return self._llm is not None


llm_service = LLMService()
