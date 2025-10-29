"""Memory control endpoints for conversation context management."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.core.rag_engine_pro import rag_engine_pro

router = APIRouter()


class MemorySettingsUpdate(BaseModel):
    """Request model for updating memory settings."""
    enabled: bool = Field(..., description="Enable or disable conversation memory")
    window_size: int = Field(..., ge=2, le=20, description="Number of Q&A pairs to retain (2, 5, 10, or 20)")


class MemorySettingsResponse(BaseModel):
    """Response model for memory settings."""
    enabled: bool
    window_size: int
    current_messages: int
    conversation_pairs: int
    at_capacity: bool


@router.get("/memory/settings", response_model=MemorySettingsResponse)
async def get_memory_settings():
    """Get current memory configuration and statistics."""
    stats = rag_engine_pro.get_memory_stats()
    return MemorySettingsResponse(**stats)


@router.post("/memory/settings", response_model=MemorySettingsResponse)
async def update_memory_settings(settings: MemorySettingsUpdate):
    """Update memory configuration.
    
    Args:
        settings: New memory settings with enabled flag and window size
    
    Returns:
        Updated memory settings and statistics
    """
    try:
        # Validate window size
        if settings.window_size not in [2, 5, 10, 20]:
            raise HTTPException(
                status_code=400,
                detail="Window size must be one of: 2, 5, 10, or 20 message pairs"
            )
        
        # Apply settings
        rag_engine_pro.set_memory_enabled(settings.enabled)
        rag_engine_pro.set_memory_window_size(settings.window_size)
        
        # Return updated stats
        stats = rag_engine_pro.get_memory_stats()
        return MemorySettingsResponse(**stats)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update memory settings: {str(e)}")


@router.post("/memory/clear")
async def clear_memory():
    """Clear all conversation history from memory.
    
    Returns:
        Success message with updated memory statistics
    """
    try:
        rag_engine_pro.clear_memory()
        stats = rag_engine_pro.get_memory_stats()
        
        return {
            "message": "Conversation memory cleared successfully",
            "memory_stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear memory: {str(e)}")
