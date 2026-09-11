"""
SupplyGuard API Router Registration.
"""

from fastapi import APIRouter

from backend.routers.health import router as health_router

# Central API router mounted under settings.api_prefix (e.g. /api/v1)
api_router = APIRouter()
api_router.include_router(health_router)

__all__ = ["api_router"]
