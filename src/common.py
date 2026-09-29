"""Shared helpers for all model notebooks (Stage 6 + 7).
Everyone imports this file, so every model uses the SAME split, CV folds and metrics
-> a fair comparison. Do NOT edit on your model branch; change it only on main and tell the team.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import (GroupShuffleSplit, train_test_split, StratifiedKFold,
                                     StratifiedGroupKFold, cross_validate, RandomizedSearchCV)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (classification_report, confusion_matrix,
                             ConfusionMatrixDisplay, f1_score, recall_score, accuracy_score)
from sklearn.utils.class_weight import compute_sample_weight
from preprocessing import build_preprocessor
from xgboost import XGBClassifier

# ------------------------------------------------------------------ CONFIG (edit on main only)
ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs"
TARGET = "readmitted"
GROUP_COL = "patient_nbr"
ID_COLUMNS = ["encounter_id", "patient_nbr"]
RANDOM_STATE = 42
N_SPLITS = 5
RESULTS_DIR = ROOT / "outputs" / "results"
MODELS_DIR = ROOT / "outputs" / "models"
FIGS_DIR = ROOT / "outputs" / "figures"
for _d in (RESULTS_DIR, MODELS_DIR, FIGS_DIR):
    _d.mkdir(parents=True, exist_ok=True)


def slug(name):
    return name.lower().replace(" ", "_")


# ------------------------------------------------------------------ data + split
def load_and_split(test_size=None):
    """Reads the patient-level split made by preprocessing.py (outputs/train_raw_split.csv / test_raw_split.csv).
    Returns the RAW train/test features (no preprocessing applied): preprocessing lives inside each model's
    Pipeline and is refitted in every CV fold. CV is stratified and grouped by patient."""
    train_df = pd.read_csv(OUT_DIR / "train_raw_split.csv", keep_default_na=False, na_values=["?"], low_memory=False)
    test_df = pd.read_csv(OUT_DIR / "test_raw_split.csv", keep_default_na=False, na_values=["?"], low_memory=False)
    le = LabelEncoder().fit(train_df[TARGET])
    y_train, y_test = le.transform(train_df[TARGET]), le.transform(test_df[TARGET])
    g_train = train_df[GROUP_COL]
    X_train = train_df.drop(columns=[TARGET] + ID_COLUMNS)
    X_test = test_df.drop(columns=[TARGET] + ID_COLUMNS)
    cv = StratifiedGroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    return X_train, X_test, y_train, y_test, g_train, cv, list(le.classes_)


def make_preprocessor(X_train=None, scale=True):
    """Unfitted preprocessor for use INSIDE a Pipeline (X_train is accepted only for backward compatibility)."""
    return build_preprocessor(scale=scale)


class BalancedXGB(XGBClassifier):
    """XGBoost has no class_weight for multiclass, so weights are computed inside fit()."""
    def fit(self, X, y, **kwargs):
        kwargs["sample_weight"] = compute_sample_weight("balanced", y)
        return super().fit(X, y, **kwargs)


# ------------------------------------------------------------------ evaluation
SCORING = {"macro_f1": "f1_macro", "weighted_f1": "f1_weighted",
           "macro_recall": "recall_macro", "accuracy": "accuracy"}


def baseline_cv(pipe, X_train, y_train, g_train, cv):
    """Stratified (grouped) CV on the TRAIN set. Train-vs-CV gap = overfitting check."""
    res = cross_validate(pipe, X_train, y_train, cv=cv, groups=g_train, scoring=SCORING,
                         return_train_score=True, n_jobs=1)
    return {"cv_macro_f1": float(res["test_macro_f1"].mean()),
            "cv_macro_f1_std": float(res["test_macro_f1"].std()),
            "train_macro_f1": float(res["train_macro_f1"].mean()),
            "cv_weighted_f1": float(res["test_weighted_f1"].mean()),
            "cv_macro_recall": float(res["test_macro_recall"].mean()),
            "cv_accuracy": float(res["test_accuracy"].mean())}


def tune(pipe, space, X_train, y_train, g_train, cv, n_iter=15):
    """Randomised search, optimised on macro-F1 (NOT accuracy - the classes are imbalanced)."""
    search = RandomizedSearchCV(pipe, space, n_iter=n_iter, cv=cv, scoring="f1_macro",
                                n_jobs=1, random_state=RANDOM_STATE, verbose=1)
    search.fit(X_train, y_train, groups=g_train)
    return search


def finalize(name, baseline, search, X_test, y_test, class_names):
    """Test-set evaluation of the tuned model + save results/model/figure for the comparison notebook.
    The test set is only REPORTED here; the final model is chosen by CV score (see compare_models)."""
    model = search.best_estimator_
    pred = model.predict(X_test)
    report = classification_report(y_test, pred, target_names=[str(c) for c in class_names],
                                   output_dict=True, zero_division=0)
    print(classification_report(y_test, pred, target_names=[str(c) for c in class_names],
                                digits=3, zero_division=0))
    disp = ConfusionMatrixDisplay(confusion_matrix(y_test, pred, normalize="true"),
                                  display_labels=[str(c) for c in class_names])
    disp.plot(cmap="Blues", values_format=".2f")
    plt.title(f"{name} - normalised confusion matrix")
    plt.savefig(FIGS_DIR / f"{slug(name)}_confusion.png", dpi=150, bbox_inches="tight")
    plt.show()

    out = {"model": name, **{f"baseline_{k}": v for k, v in baseline.items()},
           "tuned_cv_macro_f1": float(search.best_score_),
           "best_params": {k: (v if isinstance(v, (int, float, str, bool, type(None))) else str(v))
                           for k, v in search.best_params_.items()},
           "test_macro_f1": float(f1_score(y_test, pred, average="macro")),
           "test_weighted_f1": float(f1_score(y_test, pred, average="weighted")),
           "test_macro_recall": float(recall_score(y_test, pred, average="macro")),
           "test_accuracy": float(accuracy_score(y_test, pred)),
           "per_class_report": report}
    (RESULTS_DIR / f"{slug(name)}.json").write_text(json.dumps(out, indent=2))
    joblib.dump(model, MODELS_DIR / f"{slug(name)}.joblib")
    print(f"Saved results + model for {name}.")
    return out


def transformed_feature_names(fitted_pipeline):
    return fitted_pipeline.named_steps["pre"].get_feature_names_out()
