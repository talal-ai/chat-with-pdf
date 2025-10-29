"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Groq Settings
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_temperature: float = 0.3
    
    # OpenAI Settings (for embeddings)
    openai_api_key: str = ""
    
    # Pinecone Settings
    pinecone_api_key: str = ""
    pinecone_environment: str = "us-west1-gcp"
    pinecone_index_name: str = "aaoifi-standards"
    
    # Embedding Settings
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    
    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_retrieval: int = 10  # Retrieve more to filter duplicates
    
    # API Settings
    api_title: str = "AAOIFI RAG Chatbot API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
