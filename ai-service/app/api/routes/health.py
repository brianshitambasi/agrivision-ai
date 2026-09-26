from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.schemas.response import HealthResponse
from app.core.config import settings

router = APIRouter()


@router.api_route("/health", methods=["GET", "HEAD"], response_model=HealthResponse)
async def health_check(request: Request):
    if request.method == "HEAD":
        return JSONResponse(content=None, status_code=200)
    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        version=settings.VERSION,
    )
