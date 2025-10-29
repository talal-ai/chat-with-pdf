# RAG Chatbot Backend

Production-ready RAG chatbot for AAOIFI Sharia Standards using FastAPI, LangChain, Groq, and Pinecone.

## Setup

1. Install Poetry: `pip install poetry`
2. Install dependencies: `poetry install`
3. Copy `.env.example` to `.env` and add your API keys
4. Process PDF: `poetry run python upload_pdf.py`
5. Run server: `poetry run uvicorn app.main:app --reload`

## API Endpoints

- `POST /api/v1/chat` - Chat with the RAG system
- `POST /api/v1/clear` - Clear conversation history  
- `GET /api/v1/health` - Health check
- `GET /docs` - Interactive API documentation

## Tech Stack

- FastAPI - Modern async API
- LangChain - RAG orchestration
- Groq - Free LLM inference
- Pinecone - Vector database
- OpenAI Embeddings - Text embeddings
