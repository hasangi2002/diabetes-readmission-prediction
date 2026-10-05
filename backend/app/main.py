from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .model_loader import ModelLoadError, load_model_bundle
from .predictor import predict
from .schemas import PredictionRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Diabetes Readmission Prediction API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/api/model-info")
def model_info() -> dict:
    try:
        _, info = load_model_bundle()
    except ModelLoadError as exc:
        logger.exception("Model bundle unavailable")
        raise HTTPException(status_code=503, detail="Prediction model is currently unavailable") from exc
    return {
        "model_name": info["model"],
        "task": "Multiclass diabetes readmission prediction",
        "class_labels": info["classes"],
        "cv_macro_f1": info["cv"]["cv_macro_f1"],
        "test_macro_f1": info["test"]["macro_f1"],
    }


@app.post("/api/predict")
def make_prediction(request: PredictionRequest) -> dict:
    try:
        return predict(request)
    except ModelLoadError as exc:
        logger.exception("Model bundle unavailable")
        raise HTTPException(status_code=503, detail="Prediction model is currently unavailable") from exc
    except RuntimeError as exc:
        logger.exception("Prediction request failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected prediction failure")
        raise HTTPException(status_code=500, detail="Prediction could not be completed") from exc
