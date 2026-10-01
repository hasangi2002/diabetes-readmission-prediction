"""Single source of truth for data preparation (Stage 3-4 fixes).

Used by: the preprocessing notebook, the model notebooks (via common.py) and later the backend.

Fixes applied here
  1. 'None' in A1Cresult / max_glu_serum means "test not performed" - it is kept as its own category
     (pandas would otherwise turn it into NaN). Only '?' is treated as missing.
  2. Encounters where the patient died or went to hospice cannot be readmitted -> excluded.
  3. Preprocessing is exposed as an unfitted sklearn ColumnTransformer (build_preprocessor) so it can be
     placed INSIDE a Pipeline and refitted in every CV fold.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ID_COLUMNS = ["encounter_id", "patient_nbr"]
TARGET = "readmitted"
DROP_COLUMNS = ["weight"]                              # 96.9% missing
# Expired (11, 19, 20, 21) and hospice (13, 14) discharge dispositions - readmission is not possible
EXCLUDED_DISCHARGE_CODES = [11, 13, 14, 19, 20, 21]
RANDOM_STATE = 42

AGE_MIDPOINTS = {"[0-10)": 5, "[10-20)": 15, "[20-30)": 25, "[30-40)": 35, "[40-50)": 45,
                 "[50-60)": 55, "[60-70)": 65, "[70-80)": 75, "[80-90)": 85, "[90-100)": 95}


def load_raw(path):
    """FIX 1: only '?' is missing. 'None' (test not performed) stays a real category."""
    return pd.read_csv(path, keep_default_na=False, na_values=["?"], low_memory=False)


def exclude_expired_hospice(df):
    """FIX 2: drop encounters that ended in death or hospice discharge."""
    return df[~df["discharge_disposition_id"].isin(EXCLUDED_DISCHARGE_CODES)].copy()


def add_features(df):
    """Row-wise feature engineering (no statistics are learned, so it cannot leak).
    The backend must call this on user input before calling pipeline.predict()."""
    df = df.copy()
    df["total_previous_visits"] = (df["number_outpatient"].fillna(0) + df["number_emergency"].fillna(0)
                                   + df["number_inpatient"].fillna(0))
    df["has_previous_inpatient_visit"] = (df["number_inpatient"].fillna(0) > 0).astype(int)
    df["total_procedures"] = df["num_lab_procedures"].fillna(0) + df["num_procedures"].fillna(0)
    df["age_midpoint"] = df["age"].map(AGE_MIDPOINTS)
    return df


def prepare_dataframe(raw_path):
    """raw csv -> cleaned dataframe with engineered features (still contains ids and target)."""
    df = load_raw(raw_path)
    df = df.drop(columns=[c for c in DROP_COLUMNS if c in df.columns])
    df = exclude_expired_hospice(df)
    return add_features(df)


def split_by_patient(df, test_size=0.20):
    """Patient-level hold-out split: one patient never appears in both train and test."""
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=RANDOM_STATE)
    tr, te = next(splitter.split(df, y=df[TARGET], groups=df["patient_nbr"]))
    return df.iloc[tr].copy(), df.iloc[te].copy()


def build_preprocessor(scale=True):
    """FIX 3: UNFITTED preprocessor. Put it inside a Pipeline so it is refitted on each CV training fold.
    Categorical missing ('?') becomes its own 'Unknown' category (missingness can be informative)."""
    num_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale:
        num_steps.append(("scaler", StandardScaler()))
    return ColumnTransformer(
        transformers=[
            ("numeric", Pipeline(num_steps), make_column_selector(dtype_include=np.number)),
            ("categorical", Pipeline([
                ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
                ("onehot", OneHotEncoder(handle_unknown="ignore"))]),
             make_column_selector(dtype_exclude=np.number)),
        ],
        remainder="drop",
    )


def make_splits(raw_path, out_dir):
    """Recreate outputs/train_raw_split.csv and outputs/test_raw_split.csv (with the fixes applied)."""
    out_dir = Path(out_dir); out_dir.mkdir(exist_ok=True, parents=True)
    df = prepare_dataframe(raw_path)
    train_df, test_df = split_by_patient(df)
    train_df.to_csv(out_dir / "train_raw_split.csv", index=False)
    test_df.to_csv(out_dir / "test_raw_split.csv", index=False)
    overlap = len(set(train_df.patient_nbr) & set(test_df.patient_nbr))
    print(f"train {train_df.shape}, test {test_df.shape}, patient overlap = {overlap}")
    print("train classes:", train_df[TARGET].value_counts(normalize=True).round(3).to_dict())
    return train_df, test_df


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    make_splits(root / "data" / "diabetic_data.csv", root / "outputs")
