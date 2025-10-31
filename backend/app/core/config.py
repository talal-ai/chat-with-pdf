"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider Selection (groq or openai)
    llm_provider: str = "groq"  # Default to groq, set to "openai" to use OpenAI

    # Groq Settings
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_temperature: float = 0.3

    # OpenAI Settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"  # or gpt-4, gpt-4-turbo, gpt-3.5-turbo
    openai_temperature: float = 0.3

    # Pinecone Settings
    pinecone_api_key: str = ""
    pinecone_environment: str = "us-west1-gcp"
    pinecone_index_name: str = "aaoifi-standards"

    # Embedding Settings
    # Use a HuggingFace sentence-transformers model for local/free embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    # Dimension for the chosen embedding model (all-MiniLM-L6-v2 -> 384)
    embedding_dimension: int = 384

    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_retrieval: int = 10  # Retrieve more to filter duplicates

    # API Settings
    api_title: str = "AAOIFI RAG Chatbot API"
    api_version: str = "1.0.0"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


# Global settings instance
settings = Settings()
