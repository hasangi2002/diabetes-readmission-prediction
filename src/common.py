"""Shared helpers for ALL model notebooks (Stage 6 + 7).

Every model uses the SAME data split, the SAME 5 patient-grouped stratified folds and the SAME metrics, so the
comparison is fair. Change this file only on `main` (never on a model branch) and tell the team.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import json, time, warnings
from dataclasses import dataclass, field
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.experimental import enable_halving_search_cv  # noqa: F401  (needed for HalvingRandomSearchCV)
from sklearn.model_selection import (StratifiedGroupKFold, GridSearchCV, RandomizedSearchCV,
                                     HalvingRandomSearchCV)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (accuracy_score, average_precision_score, classification_report,
                             confusion_matrix, ConfusionMatrixDisplay, f1_score, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score, roc_curve)

from preprocessing import build_preprocessor, ID_COLUMNS, TARGET
from estimators import BalancedXGB

# ------------------------------------------------------------------ configuration
ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs"
RESULTS_DIR = OUT_DIR / "results"
MODELS_DIR = OUT_DIR / "models"
FIGS_DIR = OUT_DIR / "figures"
GROUP_COL = "patient_nbr"
RANDOM_STATE = 42
N_SPLITS = 5
for _d in (RESULTS_DIR, MODELS_DIR, FIGS_DIR):
    _d.mkdir(parents=True, exist_ok=True)


def slug(text):
    return "".join(ch if ch.isalnum() else "_" for ch in text.lower()).strip("_")


# ------------------------------------------------------------------ data
def load_and_split():
    """Reads the patient-level split made by preprocessing.py / the Stage 3-4 notebook.
    Returns RAW features: preprocessing lives inside every model's Pipeline and is refitted in each CV fold."""
    kw = dict(keep_default_na=False, na_values=["?"], low_memory=False)
    train_df = pd.read_csv(OUT_DIR / "train_raw_split.csv", **kw)
    test_df = pd.read_csv(OUT_DIR / "test_raw_split.csv", **kw)
    le = LabelEncoder().fit(train_df[TARGET])          # classes: 0 = '<30', 1 = '>30', 2 = 'NO'
    y_train, y_test = le.transform(train_df[TARGET]), le.transform(test_df[TARGET])
    g_train = train_df[GROUP_COL]
    X_train = train_df.drop(columns=[TARGET] + ID_COLUMNS)
    X_test = test_df.drop(columns=[TARGET] + ID_COLUMNS)
    cv = StratifiedGroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    return X_train, X_test, y_train, y_test, g_train, cv, list(le.classes_)


def make_preprocessor(scale=True):
    """Unfitted preprocessor for use INSIDE a Pipeline (fitted on training folds only -> no leakage)."""
    return build_preprocessor(scale=scale)


def patient_subsample(X, y, g, frac, seed=RANDOM_STATE):
    """Random sample of PATIENTS (all their encounters stay together)."""
    if frac >= 1:
        return X, y, g
    rng = np.random.RandomState(seed)
    patients = g.unique()
    keep = set(rng.choice(patients, size=max(int(len(patients) * frac), 50), replace=False))
    mask = g.isin(keep).values
    return X.loc[mask].reset_index(drop=True), y[mask], g.loc[mask].reset_index(drop=True)


# ------------------------------------------------------------------ metrics
def compute_metrics(y_true, proba):
    """All metrics used in the project. Class 0 is '<30' (early readmission, the clinically important class)."""
    pred = proba.argmax(axis=1)
    return {
        "macro_f1": f1_score(y_true, pred, average="macro"),
        "weighted_f1": f1_score(y_true, pred, average="weighted"),
        "macro_recall": recall_score(y_true, pred, average="macro"),      # = balanced accuracy
        "macro_precision": precision_score(y_true, pred, average="macro", zero_division=0),
        "accuracy": accuracy_score(y_true, pred),
        "roc_auc_ovr": roc_auc_score(y_true, proba, multi_class="ovr", average="macro"),
        "pr_auc_lt30": average_precision_score((y_true == 0).astype(int), proba[:, 0]),
        "recall_lt30": recall_score(y_true, pred, labels=[0], average="macro", zero_division=0),
        "precision_lt30": precision_score(y_true, pred, labels=[0], average="macro", zero_division=0),
        "f1_lt30": f1_score(y_true, pred, labels=[0], average="macro", zero_division=0),
    }


def cv_evaluate(pipe, X, y, g, cv):
    """5-fold stratified, patient-grouped cross-validation on the TRAINING set (same folds for every model).
    train_macro_f1 vs cv_macro_f1 shows over-fitting."""
    rows, train_f1, fit_times = [], [], []
    for tr, va in cv.split(X, y, g):
        model = clone(pipe)
        t0 = time.time()
        model.fit(X.iloc[tr], y[tr])
        fit_times.append(time.time() - t0)
        rows.append(compute_metrics(y[va], model.predict_proba(X.iloc[va])))
        train_f1.append(f1_score(y[tr], model.predict(X.iloc[tr]), average="macro"))
    df = pd.DataFrame(rows)
    out = {f"cv_{c}": float(df[c].mean()) for c in df.columns}
    out["cv_macro_f1_std"] = float(df["macro_f1"].std())
    out["cv_pr_auc_lt30_std"] = float(df["pr_auc_lt30"].std())
    out["train_macro_f1"] = float(np.mean(train_f1))
    out["fit_time_s"] = float(np.mean(fit_times))
    out["cv_macro_f1_folds"] = [float(v) for v in df["macro_f1"]]
    return out


baseline_cv = cv_evaluate   # backward-compatible name


def compare_table(baseline, tuned):
    keys = [("cv_macro_f1", "CV macro-F1 (main metric)"), ("cv_macro_recall", "CV macro-recall"),
            ("cv_accuracy", "CV accuracy"), ("cv_roc_auc_ovr", "CV ROC-AUC (OvR, macro)"),
            ("cv_pr_auc_lt30", "CV PR-AUC for <30"), ("cv_recall_lt30", "CV recall for <30"),
            ("train_macro_f1", "Train macro-F1 (over-fit check)"), ("fit_time_s", "Fit time per fold (s)")]
    t = pd.DataFrame({"baseline": {n: baseline[k] for k, n in keys},
                      "tuned": {n: tuned[k] for k, n in keys}})
    t["change"] = t["tuned"] - t["baseline"]
    return t.round(4)


# ------------------------------------------------------------------ experiment log (Stage 6: "record experiments")
def _log_path(name):
    return RESULTS_DIR / f"{slug(name)}_experiments.csv"


def reset_log(name):
    _log_path(name).unlink(missing_ok=True)


def run_experiment(name, experiment, setting, pipe, X, y, g, cv, note=""):
    """Cross-validate one configuration and append the result to this model's experiment log (CSV)."""
    m = cv_evaluate(pipe, X, y, g, cv)
    row = {"model": name, "experiment": experiment, "setting": str(setting),
           "cv_macro_f1": m["cv_macro_f1"], "train_macro_f1": m["train_macro_f1"],
           "cv_macro_recall": m["cv_macro_recall"], "cv_accuracy": m["cv_accuracy"],
           "cv_roc_auc_ovr": m["cv_roc_auc_ovr"], "cv_pr_auc_lt30": m["cv_pr_auc_lt30"],
           "fit_time_s": m["fit_time_s"], "note": note, "n_rows": len(X),
           "logged_at": time.strftime("%Y-%m-%d %H:%M")}
    p = _log_path(name)
    pd.DataFrame([row]).to_csv(p, mode="a", header=not p.exists(), index=False)
    print(f"[{experiment}] {setting}: macro-F1={m['cv_macro_f1']:.4f} (train {m['train_macro_f1']:.4f})")
    return m


def show_experiments(name, experiment=None):
    df = pd.read_csv(_log_path(name))
    if experiment:
        df = df[df["experiment"] == experiment]
    return df[["experiment", "setting", "cv_macro_f1", "train_macro_f1", "cv_macro_recall",
               "cv_roc_auc_ovr", "cv_pr_auc_lt30", "fit_time_s"]].round(4).reset_index(drop=True)


def plot_sweep(df, title, name):
    ax = df.plot(x="setting", y=["train_macro_f1", "cv_macro_f1"], marker="o", figsize=(7, 3.8), rot=20)
    ax.set_ylabel("macro-F1"); ax.set_title(title)
    plt.tight_layout()
    plt.savefig(FIGS_DIR / f"{slug(name)}_{slug(title)}.png", dpi=150)
    plt.show()


def sweep(name, experiment, values, factory, X, y, g, cv, note=""):
    """Run one experiment for each value; factory(value) must return a Pipeline."""
    for v in values:
        run_experiment(name, experiment, f"{experiment}={v}", factory(v), X, y, g, cv, note)
    df = show_experiments(name, experiment)
    plot_sweep(df, experiment, name)
    return df


# ------------------------------------------------------------------ hyper-parameter search (Stage 7)
@dataclass
class TuneResult:
    best_estimator_: object
    best_params_: dict
    best_score_: float
    method: str
    sample_frac: float
    search_time_s: float
    cv_results: pd.DataFrame = field(repr=False)


def tune(pipe, space, X, y, g, cv, method="random", n_iter=15, sample_frac=1.0):
    """method: 'grid' | 'random' | 'halving'. Scored on macro-F1 with the shared grouped folds.
    If sample_frac < 1 the search runs on a patient-level sample (fast) and the best configuration is then
    refitted on ALL training data."""
    Xs, ys, gs = patient_subsample(X, y, g, sample_frac)
    common = dict(cv=cv, scoring="f1_macro", n_jobs=1, verbose=1)
    if method == "grid":
        search = GridSearchCV(pipe, space, **common)
    elif method == "random":
        search = RandomizedSearchCV(pipe, space, n_iter=n_iter, random_state=RANDOM_STATE, **common)
    elif method == "halving":
        search = HalvingRandomSearchCV(pipe, space, n_candidates=n_iter, factor=3,
                                       random_state=RANDOM_STATE, **common)
    else:
        raise ValueError("method must be 'grid', 'random' or 'halving'")
    t0 = time.time()
    search.fit(Xs, ys, groups=gs)
    elapsed = time.time() - t0
    best = search.best_estimator_ if sample_frac >= 1 else clone(pipe).set_params(**search.best_params_).fit(X, y)
    res = pd.DataFrame(search.cv_results_).sort_values("rank_test_score")
    return TuneResult(best, search.best_params_, float(search.best_score_), method, sample_frac, elapsed, res)


def top_configs(tune_res, n=5):
    cols = [c for c in tune_res.cv_results.columns if c.startswith("param_")] + ["mean_test_score", "std_test_score"]
    return tune_res.cv_results[cols].head(n).round(4)


# ------------------------------------------------------------------ interpretation helpers
def _original_feature(encoded, columns):
    name = encoded.split("__", 1)[1] if "__" in encoded else encoded
    if name in columns:
        return name
    matches = [c for c in columns if name.startswith(c + "_")]
    return max(matches, key=len) if matches else name


def feature_importance_table(pipe, columns, class_index=None):
    """Importance (trees) or coefficient (linear) per ENCODED feature, mapped back to the ORIGINAL column."""
    model = pipe.named_steps["m"]
    names = np.asarray(pipe.named_steps["pre"].get_feature_names_out())
    if "sel" in pipe.named_steps:
        names = names[pipe.named_steps["sel"].get_support()]
    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
    else:
        values = np.abs(model.coef_).mean(axis=0) if class_index is None else model.coef_[class_index]
    df = pd.DataFrame({"feature": names, "value": values})
    df["original"] = [_original_feature(n, list(columns)) for n in names]
    return df


def top_original_features(table, n=15):
    return table.assign(value=table["value"].abs()).groupby("original")["value"].sum().sort_values(ascending=False).head(n)


def plot_top_features(series, title, name):
    ax = series.iloc[::-1].plot(kind="barh", figsize=(7, 5), title=title)
    ax.set_xlabel("importance (summed over the one-hot columns of each original feature)")
    plt.tight_layout(); plt.savefig(FIGS_DIR / f"{slug(name)}_importance.png", dpi=150); plt.show()


# ------------------------------------------------------------------ final test-set evaluation + saving
def finalize(name, baseline, tuned, tune_res, X_test, y_test, class_names, notes=""):
    """Evaluate the tuned model on the untouched test set (reported ONCE), save figures, JSON and model."""
    model = tune_res.best_estimator_
    proba = model.predict_proba(X_test)
    pred = proba.argmax(axis=1)
    labels = [str(c) for c in class_names]
    test = compute_metrics(y_test, proba)
    print(classification_report(y_test, pred, target_names=labels, digits=3, zero_division=0))

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    ConfusionMatrixDisplay(confusion_matrix(y_test, pred, normalize="true"), display_labels=labels).plot(
        ax=axes[0], cmap="Blues", values_format=".2f", colorbar=False)
    axes[0].set_title("Confusion matrix (row-normalised)")
    p, r, _ = precision_recall_curve((y_test == 0).astype(int), proba[:, 0])
    axes[1].plot(r, p); axes[1].axhline((y_test == 0).mean(), ls="--", c="grey")
    axes[1].set_title(f"PR curve for '<30' (AP={test['pr_auc_lt30']:.3f})"); axes[1].set_xlabel("recall"); axes[1].set_ylabel("precision")
    for i, lab in enumerate(labels):
        fpr, tpr, _ = roc_curve((y_test == i).astype(int), proba[:, i])
        axes[2].plot(fpr, tpr, label=lab)
    axes[2].plot([0, 1], [0, 1], "--", c="grey"); axes[2].legend(); axes[2].set_title("ROC (one-vs-rest)")
    plt.suptitle(f"{name} - test set"); plt.tight_layout()
    plt.savefig(FIGS_DIR / f"{slug(name)}_test_evaluation.png", dpi=150); plt.show()

    payload = {"model": name, "notes": notes,
               "baseline": baseline, "tuned": tuned,
               "search": {"method": tune_res.method, "sample_frac": tune_res.sample_frac,
                          "search_time_s": tune_res.search_time_s, "best_search_score": tune_res.best_score_,
                          "best_params": {k: (v if isinstance(v, (int, float, str, bool, type(None))) else str(v))
                                          for k, v in tune_res.best_params_.items()}},
               "test": {k: float(v) for k, v in test.items()},
               "per_class_report": classification_report(y_test, pred, target_names=labels,
                                                         output_dict=True, zero_division=0),
               "class_names": labels}
    (RESULTS_DIR / f"{slug(name)}.json").write_text(json.dumps(payload, indent=2))
    joblib.dump(model, MODELS_DIR / f"{slug(name)}.joblib", compress=3)
    print(f"Saved outputs/results/{slug(name)}.json and outputs/models/{slug(name)}.joblib")
    return payload


def dummy_baselines(X, y, g, cv):
    """What a model that ignores the features would score - the bar every model must clear."""
    out = {}
    for label, strat in [("Majority class", "prior"), ("Random (class priors)", "stratified")]:
        out[label] = cv_evaluate(Pipeline([("m", DummyClassifier(strategy=strat, random_state=RANDOM_STATE))]),
                                 X[["time_in_hospital"]], y, g, cv)
    return out