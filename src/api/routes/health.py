"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def health_check():
    """Check system health."""
    return {
        "status": "healthy",
        "message": "Autonomous Trading System is operational",
        "version": "2.0.0"
    }


@router.get("/ready")
async def ready_check():
    """Check if system is ready."""
    return {
        "ready": True,
        "message": "System is ready for trading"
    }
