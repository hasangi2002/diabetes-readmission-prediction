from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .model_loader import load_model_bundle
from .schemas import PredictionRequest

logger = logging.getLogger(__name__)
OUTCOMES = {
    "<30": "Readmitted within 30 days",
    ">30": "Readmitted after 30 days",
    "NO": "Not readmitted",
}


def predict(request: PredictionRequest) -> dict:
    model, metadata = load_model_bundle()
    # Use exactly the repository's row-wise feature logic. Reimplementing it here
    # risks training/serving skew in these four model input columns.
    from src.preprocessing import add_features

    row = request.model_dump(by_alias=True)
    frame = pd.DataFrame([row])
    # preprocessing.load_raw treats '?' as missing while preserving 'None' as a
    # real category; mirror that CSV parsing behavior for the API's raw values.
    frame = frame.replace("?", np.nan)
    featured = add_features(frame)

    # Metadata preserves the training column order and contains the engineered fields.
    columns = metadata["feature_columns"]
    try:
        prediction = int(model.predict(featured.loc[:, columns])[0])
        probabilities = model.predict_proba(featured.loc[:, columns])[0]
    except Exception as exc:
        logger.exception("Saved model inference failed")
        raise RuntimeError("Prediction could not be generated for this input") from exc

    labels = metadata["classes"]
    if prediction not in range(len(labels)) or len(probabilities) != len(labels):
        raise RuntimeError("Model returned an unexpected class result")
    predicted_class = labels[prediction]
    return {
        "predicted_class": predicted_class,
        "predicted_outcome": OUTCOMES[predicted_class],
        "probability_lt30": float(probabilities[0]),
        "probability_gt30": float(probabilities[1]),
        "probability_no": float(probabilities[2]),
    }
