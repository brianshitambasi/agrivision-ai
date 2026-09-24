from fastapi import APIRouter
from app.schemas.response import HealthResponse
from app.core.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", service=settings.APP_NAME, version=settings.VERSION)
