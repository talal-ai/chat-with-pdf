"""Health check endpoints."""

from fastapi import APIRouter, Query
from app.schemas.chat import HealthResponse
from app.core.config import settings
from app.services.llm_service import llm_service
from app.services.vector_store import vector_store

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    deep: bool = Query(False, description="Perform deep health check including external services")
):
    """Health check endpoint with optional deep checks for external services."""
    if not deep:
        return HealthResponse(status="healthy", version=settings.api_version)

    # Deep check - verify external services
    llm_info = llm_service.get_provider_info()
    services_status = {
        "llm_service": llm_service.is_available(),
        "vector_store": vector_store.is_available(),
        "llm_provider": llm_info["provider"],
        "llm_model": llm_info.get("model", "unknown"),
        "llm_status": llm_info["status"],
    }

    all_healthy = all([services_status["llm_service"], services_status["vector_store"]])
    status = "healthy" if all_healthy else "degraded"

    return HealthResponse(status=status, version=settings.api_version)
