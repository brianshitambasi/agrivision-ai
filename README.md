# 🌱 AgriVision AI

**Automated Computer Vision System for Early-Stage Crop Pest and Disease Detection**

An honest, end-to-end AI system for diagnosing plant diseases from leaf images.

---

## 📊 Model Performance (Measured, Not Claimed)

| Metric | Value |
|--------|-------|
| Architecture | ResNet18 (transfer learning) |
| Classes | 15 (Pepper, Potato, Tomato) |
| Training images | 14,440 |
| Test accuracy | 88.65% (on 3,109 held-out images) |
| Confidence threshold | 70% (below returns "Unknown") |
| Accuracy when confident (>70%) | 97.0% |

### Per-class F1 scores

- Tomato Yellow Leaf Curl Virus: 0.968
- Pepper Healthy: 0.962
- Potato Early Blight: 0.938
- Tomato Healthy: 0.925
- Tomato Bacterial Spot: 0.918
- Potato Late Blight: 0.903
- Potato Healthy: 0.894
- Tomato Late Blight: 0.872
- Tomato Mosaic Virus: 0.862
- Pepper Bacterial Spot: 0.860
- Tomato Septoria Leaf Spot: 0.847
- Tomato Leaf Mold: 0.842
- Tomato Spider Mites: 0.841
- Tomato Target Spot: 0.765
- Tomato Early Blight: 0.710

---

## Architecture

React (port 3000) -> Node (port 5000) -> FastAPI (port 8000) -> PyTorch ResNet18

Node also talks to MongoDB.

---

## Features

- Real AI inference (not mocked)
- JWT authentication
- Diagnosis history per user (MongoDB)
- Multi-format image upload (JPEG, PNG, WebP, GIF, BMP, TIFF)
- Confidence thresholding (returns "Unknown" below 70%)
- Crop-specific disease metadata
- Symptom descriptions
- Conservative treatment recommendations
- Clear disclaimers

---

## Project Structure

- frontend/     React CRA
- backend/      Node/Express + MongoDB + JWT
- ai-service/   FastAPI + PyTorch
- datasets/     PlantVillage raw + processed
- docs/         Documentation

---

## Quick Start

### Start AI Service

    cd ai-service
    python -m venv venv
    source venv/Scripts/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000

### Start Backend

    cd backend
    npm install
    npm start

### Start Frontend

    cd frontend
    npm install
    npm start

Open http://localhost:3000

---

## Evaluation

    cd ai-service
    python scripts/evaluate_model.py

Outputs: accuracy, per-class precision/recall/F1, confusion matrix, confidence analysis.

---

## Honest Reporting

- Test accuracy: 88.65% on 3,109 unseen images
- Threshold 0.7 gives 97% accuracy on high-confidence predictions
- Model does NOT detect out-of-distribution images reliably
- Softmax probability is NOT the same as real-world accuracy

All numbers come from scripts/evaluate_model.py.

---

## Keywords

AI, Computer Vision, Crop Disease Detection, PyTorch, ResNet18, FastAPI, React, MERN, Edge Computing
