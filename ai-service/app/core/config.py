import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    MODEL_PATH: str = os.getenv("MODEL_PATH", "app/models/saved/agrivision_v1.pth")
    IMG_SIZE: int = int(os.getenv("IMG_SIZE", 224))
    DEVICE: str = os.getenv("DEVICE", "cpu")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", 0.75))
    APP_NAME: str = "AgriVision AI"
    VERSION: str = "1.0.0"

settings = Settings()
