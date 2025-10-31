"""LLM service supporting both Groq and OpenAI for flexible model switching."""

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from app.core.config import settings
import structlog
from typing import Optional, Union

logger = structlog.get_logger()


class LLMService:
    """Service for LLM interactions with support for Groq and OpenAI providers."""

    def __init__(self):
        """Initialize service without creating LLM client yet."""
        self._llm: Optional[Union[ChatGroq, ChatOpenAI]] = None
        self._initialized = False
        self._initialization_error: Optional[str] = None
        self._current_provider: Optional[str] = None

        self.system_prompt = """You are a senior consultant specializing in AAOIFI Sharia Standards. Provide specific, detailed, and professionally structured responses. Extract and cite actual principles, requirements, and guidelines from the standards. Use precise terminology and cite page numbers as [Page X] for each distinct point."""

    def _initialize_llm(self):
        """Lazily initialize the LLM based on the configured provider (Groq or OpenAI)."""
        if self._initialized:
            return

        self._initialized = True
        provider = settings.llm_provider.lower()
        self._current_provider = provider

        logger.info("Initializing LLM service", provider=provider)

        if provider == "openai":
            self._initialize_openai()
        elif provider == "groq":
            self._initialize_groq()
        else:
            self._initialization_error = (
                f"Invalid LLM_PROVIDER '{provider}'. Must be 'groq' or 'openai'."
            )
            logger.error(self._initialization_error)

    def _initialize_openai(self):
        """Initialize OpenAI ChatGPT model."""
        if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
            self._initialization_error = (
                "OPENAI_API_KEY is not set. Please configure it in your .env file."
            )
            logger.error(self._initialization_error)
            return

        # List of OpenAI models in order of preference
        fallback_models = [
            settings.openai_model,
            "gpt-4o-mini",  # Most cost-effective GPT-4 model
            "gpt-4-turbo",  # High capability turbo model
            "gpt-4",  # Standard GPT-4
            "gpt-3.5-turbo",  # Fallback to GPT-3.5
        ]

        # Remove duplicates while preserving order
        seen = set()
        unique_models = []
        for model in fallback_models:
            if model not in seen:
                seen.add(model)
                unique_models.append(model)

        for model_name in unique_models:
            try:
                # ChatOpenAI reads OPENAI_API_KEY from environment by default
                # We can also pass api_key directly if needed
                self._llm = ChatOpenAI(
                    model=model_name,
                    temperature=settings.openai_temperature,
                    api_key=settings.openai_api_key,  # type: ignore
                    max_completion_tokens=2048,
                    timeout=30,
                )
                logger.info(
                    "LLMService initialized with OpenAI",
                    model=model_name,
                    provider="openai",
                )
                return
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI model {model_name}: {e}")
                continue

        self._initialization_error = "Failed to initialize any OpenAI model. Check your OPENAI_API_KEY and network connection."
        logger.error(self._initialization_error)

    def _initialize_groq(self):
        """Initialize Groq model."""
        if not settings.groq_api_key:
            self._initialization_error = (
                "GROQ_API_KEY is not set. Please configure it in your .env file."
            )
            logger.error(self._initialization_error)
            return

        # List of fallback models in order of preference (fastest first)
        fallback_models = [
            settings.groq_model,
            "llama-3.1-8b-instant",  # Fastest for quick responses
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768",
            "llama-3.2-90b-text-preview",
        ]

        # Remove duplicates while preserving order
        seen = set()
        unique_models = []
        for model in fallback_models:
            if model not in seen:
                seen.add(model)
                unique_models.append(model)

        for model_name in unique_models:
            try:
                # ChatGroq reads GROQ_API_KEY from environment by default
                # We can also pass api_key directly if needed
                self._llm = ChatGroq(
                    model=model_name,
                    temperature=settings.groq_temperature,
                    api_key=settings.groq_api_key,  # type: ignore
                    max_tokens=2048,
                    timeout=30,
                )
                logger.info("LLMService initialized with Groq", model=model_name, provider="groq")
                return
            except Exception as e:
                logger.warning(f"Failed to initialize Groq model {model_name}: {e}")
                continue

        self._initialization_error = (
            "Failed to initialize any Groq model. Check your GROQ_API_KEY and network connection."
        )
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

    def get_provider_info(self) -> dict:
        """Get information about the current LLM provider and model."""
        if not self._initialized:
            self._initialize_llm()

        if self._llm is None:
            return {
                "provider": self._current_provider or settings.llm_provider,
                "status": "unavailable",
                "error": self._initialization_error,
            }

        model_name = getattr(self._llm, "model_name", "unknown")
        return {
            "provider": self._current_provider,
            "model": model_name,
            "status": "available",
            "temperature": (
                settings.openai_temperature
                if self._current_provider == "openai"
                else settings.groq_temperature
            ),
        }


llm_service = LLMService()
