import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
from io import BytesIO
from pathlib import Path
from typing import Dict, List
from app.core.config import settings


# ============ CONFIDENCE THRESHOLD ============
LOW_CONFIDENCE_THRESHOLD = 0.70


# ============ DISEASE METADATA ============
DISEASE_INFO: Dict[str, dict] = {
    "Pepper__bell___Bacterial_spot": {
        "crop": "Pepper (Bell)",
        "disease": "Bacterial Spot",
        "symptoms": [
            "Small water-soaked spots on leaves",
            "Dark brown/black lesions with yellow halos",
            "Irregular leaf discoloration",
            "Premature leaf drop",
        ],
        "recommendation": (
            "Remove severely affected leaves. Avoid overhead watering. "
            "Apply copper-based bactericide. Improve air circulation. "
            "Consult local agricultural guidance before applying pesticides."
        ),
    },
    "Pepper__bell___healthy": {
        "crop": "Pepper (Bell)",
        "disease": "Healthy",
        "symptoms": ["No visible symptoms", "Normal green coloration"],
        "recommendation": "No action needed. Continue regular monitoring.",
    },
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Early Blight",
        "symptoms": [
            "Concentric dark rings (target-like spots)",
            "Yellowing around lesions",
            "Brown to black leaf spots",
        ],
        "recommendation": (
            "Apply chlorothalonil or mancozeb fungicide. Remove infected lower leaves. "
            "Rotate crops next season."
        ),
    },
    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy",
        "symptoms": ["No visible symptoms", "Uniform green leaves"],
        "recommendation": "No action needed. Maintain good drainage and airflow.",
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Late Blight",
        "symptoms": [
            "Water-soaked gray-green patches",
            "White fuzzy mold on leaf undersides",
            "Rapid tissue collapse",
        ],
        "recommendation": (
            "Apply mancozeb or cymoxanil immediately. Destroy severely infected plants. "
            "Highly contagious."
        ),
    },
    "Tomato__Target_Spot": {
        "crop": "Tomato",
        "disease": "Target Spot",
        "symptoms": ["Brown spots with concentric rings", "Yellow halos around lesions"],
        "recommendation": "Apply fungicide. Improve air circulation. Reduce leaf wetness.",
    },
    "Tomato__Tomato_mosaic_virus": {
        "crop": "Tomato",
        "disease": "Mosaic Virus",
        "symptoms": ["Mottled light/dark green leaves", "Leaf curling", "Stunted growth"],
        "recommendation": (
            "Remove infected plants. Disinfect tools. Control aphids. No chemical cure."
        ),
    },
    "Tomato__Tomato_YellowLeaf__Curl_Virus": {
        "crop": "Tomato",
        "disease": "Yellow Leaf Curl Virus",
        "symptoms": ["Upward leaf curling", "Yellowing leaf margins", "Stunted growth"],
        "recommendation": (
            "Remove infected plants. Control whiteflies. Use resistant varieties."
        ),
    },
    "Tomato_Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Bacterial Spot",
        "symptoms": ["Small dark water-soaked spots", "Yellow halos", "Scabby fruit lesions"],
        "recommendation": (
            "Use copper-based spray. Avoid overhead watering. Remove infected debris."
        ),
    },
    "Tomato_Early_blight": {
        "crop": "Tomato",
        "disease": "Early Blight",
        "symptoms": [
            "Dark brown spots with concentric rings",
            "Yellowing around lesions",
            "Lower leaves affected first",
        ],
        "recommendation": (
            "Apply chlorothalonil or copper fungicide. Remove lower infected leaves. "
            "Mulch soil. Rotate crops."
        ),
    },
    "Tomato_healthy": {
        "crop": "Tomato",
        "disease": "Healthy",
        "symptoms": ["No visible symptoms", "Vibrant green leaves"],
        "recommendation": "No action needed. Continue regular monitoring.",
    },
    "Tomato_Late_blight": {
        "crop": "Tomato",
        "disease": "Late Blight",
        "symptoms": [
            "Large water-soaked greasy patches",
            "White mold on leaf undersides",
            "Rapid collapse",
        ],
        "recommendation": (
            "Apply fungicide urgently (mancozeb, chlorothalonil). Isolate plant."
        ),
    },
    "Tomato_Leaf_Mold": {
        "crop": "Tomato",
        "disease": "Leaf Mold",
        "symptoms": ["Pale yellow spots on upper leaf", "Olive-green mold underneath"],
        "recommendation": "Reduce humidity. Improve ventilation. Apply copper fungicide.",
    },
    "Tomato_Septoria_leaf_spot": {
        "crop": "Tomato",
        "disease": "Septoria Leaf Spot",
        "symptoms": ["Small circular spots with dark borders", "Gray centers with black dots"],
        "recommendation": "Remove infected leaves. Apply fungicide. Avoid splashing water.",
    },
    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "crop": "Tomato",
        "disease": "Spider Mites",
        "symptoms": ["Fine webbing on leaves", "Stippled yellow speckling", "Leaf bronzing"],
        "recommendation": "Apply miticide or neem oil. Increase humidity. Introduce predatory mites.",
    },
}


# ============ MODEL LOADER ============
class ModelLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        path = Path(settings.MODEL_PATH)
        if not path.exists():
            raise FileNotFoundError(f"Model not found at {path}")
        ckpt = torch.load(path, map_location=settings.DEVICE, weights_only=False)
        self.classes: List[str] = ckpt["classes"]
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, ckpt["num_classes"])
        model.load_state_dict(ckpt["model_state_dict"])
        model.eval().to(settings.DEVICE)
        self.model = model
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        print(f"Model loaded: {ckpt['num_classes']} classes | val_acc={ckpt.get('val_acc', 0):.4f}")


def predict_image(image_bytes: bytes) -> dict:
    loader = ModelLoader()

    try:
        image = Image.open(BytesIO(image_bytes))
        # Handle animated formats (GIF) — take first frame
        if hasattr(image, "n_frames") and image.n_frames > 1:
            image.seek(0)
        # Convert any format (RGBA, P, L, CMYK, etc.) to RGB
        image = image.convert("RGB")
    except Exception as e:
        raise ValueError(
            f"Could not read image. Supported: JPEG, PNG, WebP, GIF, BMP, TIFF. Error: {e}"
        )

    tensor = loader.transform(image).unsqueeze(0).to(settings.DEVICE)

    with torch.no_grad():
        probs = torch.softmax(loader.model(tensor), dim=1)[0]

    top_p, top_i = torch.topk(probs, k=3)
    top_p = top_p.cpu().tolist()
    top_i = top_i.cpu().tolist()

    predictions = [
        {
            "label": loader.classes[i],
            "confidence": round(p, 4),
        }
        for i, p in zip(top_i, top_p)
    ]

    best = predictions[0]
    best_conf = best["confidence"]

    if best_conf < LOW_CONFIDENCE_THRESHOLD:
        return {
            "success": True,
            "crop": "Unknown",
            "disease": "Unknown / Low Confidence",
            "confidence": best_conf,
            "is_confident": False,
            "top_predictions": predictions,
            "symptoms": [],
            "recommendation": (
                "The model is not confident enough to identify this image. "
                "Try a clearer, well-lit photo of a single leaf, or consult a local expert."
            ),
            "disclaimer": (
                "This is an AI prediction, not a substitute for professional agronomic advice."
            ),
        }

    info = DISEASE_INFO.get(best["label"], {})

    return {
        "success": True,
        "crop": info.get("crop", "Unknown"),
        "disease": info.get("disease", best["label"].replace("_", " ")),
        "confidence": best_conf,
        "is_confident": True,
        "top_predictions": predictions,
        "symptoms": info.get("symptoms", []),
        "recommendation": info.get(
            "recommendation",
            "Consult your local agronomist for treatment advice.",
        ),
        "disclaimer": (
            "This is an AI prediction based on image analysis. "
            "Consult local agricultural guidance before applying pesticides."
        ),
    }
