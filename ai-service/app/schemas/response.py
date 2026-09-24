from pydantic import BaseModel
from typing import List

class PredictionItem(BaseModel):
    label: str
    confidence: float

class PredictionResponse(BaseModel):
    success: bool
    disease: str
    confidence: float
    top_predictions: List[PredictionItem]
    recommendation: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
