from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import json
import sys

import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class ModelLoadError(RuntimeError):
    """Raised when the saved model bundle cannot be read or validated."""


@lru_cache(maxsize=1)
def load_model_bundle() -> tuple[object, dict]:
    model_path = PROJECT_ROOT / "outputs" / "final_model.joblib"
    info_path = PROJECT_ROOT / "outputs" / "final_model_info.json"
    try:
        with info_path.open(encoding="utf-8") as file:
            info = json.load(file)
        model = joblib.load(model_path)
        if not hasattr(model, "predict") or not hasattr(model, "predict_proba"):
            raise ValueError("Saved object is not a prediction pipeline")
        if [str(label) for label in model.classes_] != ["0", "1", "2"]:
            raise ValueError("Saved model classes do not match the metadata label order")
        return model, info
    except Exception as exc:
        # Keep filesystem and deserialization details out of API responses.
        raise ModelLoadError("The saved prediction model could not be loaded") from exc
