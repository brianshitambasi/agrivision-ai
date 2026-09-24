from fastapi import APIRouter, File, UploadFile, HTTPException
from app.schemas.response import PredictionResponse
from app.services.predictor import predict_image
import os

router = APIRouter()

# Accept all common image formats
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/bmp",
    "image/tiff",
    "image/heic",
    "image/heif",
    "image/avif",
}

ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp",
    ".gif", ".bmp", ".tiff", ".tif",
    ".heic", ".heif", ".avif",
}

MAX_SIZE_MB = 10


@router.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    # Check by extension (more reliable than MIME from some clients)
    ext = ""
    if file.filename:
        ext = os.path.splitext(file.filename)[1].lower()

    mime_ok = file.content_type in ALLOWED_MIME_TYPES
    ext_ok = ext in ALLOWED_EXTENSIONS

    if not mime_ok and not ext_ok:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported image format: {file.content_type} ({ext}). "
                f"Please upload JPEG, PNG, WebP, GIF, BMP, TIFF, HEIC, or AVIF."
            ),
        )

    image_bytes = await file.read()

    if len(image_bytes) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {MAX_SIZE_MB}MB.",
        )

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file.")

    try:
        result = predict_image(image_bytes)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}",
        )
