"""Main FastAPI application."""

from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import structlog

from app.core.config import settings
from app.api.routes import chat, health, conversations, memory, upload

structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = structlog.get_logger()

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Server binds to port immediately, then pre-warm services in background
    import asyncio
    import time

    logger.info("🚀 Starting application...")

    # Start pre-warming in background after server is ready
    async def prewarm_services():
        """Pre-warm services in background to avoid blocking port binding."""
        await asyncio.sleep(1)  # Let server bind to port first
        
        startup_start = time.time()
        logger.info("⏳ Pre-warming services in background...")

        try:
            # Import services
            from app.services.vector_store import vector_store
            from app.services.llm_service import llm_service
            from app.core.rag_engine_pro import rag_engine_pro

            # Pre-initialize vector store (embeddings + Pinecone connection)
            logger.info("⏳ [1/3] Initializing vector store and embeddings...")
            t1 = time.time()
            vector_store._ensure_initialized()
            logger.info("✅ Vector store ready", duration_seconds=round(time.time() - t1, 2))

            # Pre-initialize LLM service
            logger.info("⏳ [2/3] Initializing LLM service...")
            t2 = time.time()
            llm_service.get_llm()  # This triggers initialization
            logger.info("✅ LLM service ready", duration_seconds=round(time.time() - t2, 2))

            # Pre-initialize RAG engine
            logger.info("⏳ [3/3] Initializing RAG engine...")
            t3 = time.time()
            rag_engine_pro._ensure_initialized()
            logger.info("✅ RAG engine ready", duration_seconds=round(time.time() - t3, 2))

            total_time = round(time.time() - startup_start, 2)
            logger.info(
                "🎉 All services pre-warmed! First response will be FAST!",
                total_startup_seconds=total_time,
            )

        except Exception as e:
            logger.error("⚠️ Service pre-warming failed", error=str(e))
            logger.warning("Application will continue but first request may be slower")

    # Schedule pre-warming as background task
    asyncio.create_task(prewarm_services())

    yield  # Application runs here

    # Shutdown: Clean up resources
    logger.info("👋 Shutting down application...")


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="RAG chatbot for AAOIFI Sharia Standards",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(conversations.router, prefix="/api/v1", tags=["conversations"])
app.include_router(memory.router, prefix="/api/v1", tags=["memory"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    logger.error("Unhandled exception", error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
async def root():
    return {"message": "AAOIFI RAG Chatbot API", "version": settings.api_version, "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
