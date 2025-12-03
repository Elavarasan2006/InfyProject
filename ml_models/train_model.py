"""
Training script for the job role prediction model.

Loads the dataset (preferring `jobrole_dataset.xlsx`), label-encodes categorical
columns, splits into train/test sets, fits an `XGBClassifier`, and stores both
the model and encoders as joblib artifacts under `ml_models/`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
MODEL_PATH = BASE_DIR / "jobrole_model.pkl"
ENCODER_PATH = BASE_DIR / "label_encoder.pkl"

DATASET_CANDIDATES = [
    PROJECT_ROOT / "jobrole_dataset.xlsx",
    PROJECT_ROOT / "ml" / "jobrole_dataset.xlsx",
    PROJECT_ROOT / "dataset.csv",
]

TARGET_COLUMN_CANDIDATES = [
    "jobrole",
    "job_role",
    "job role",
    "target",
    "role",
]


def find_dataset() -> Path:
    for candidate in DATASET_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Dataset not found. Place `jobrole_dataset.xlsx` in the project root "
        "or provide `dataset.csv`."
    )


def load_dataset() -> pd.DataFrame:
    dataset_path = find_dataset()
    if dataset_path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(dataset_path)
    else:
        df = pd.read_csv(dataset_path)
    if df.empty:
        raise ValueError(f"Dataset at {dataset_path} is empty.")
    print(f"Loaded dataset from {dataset_path}")
    return df


def infer_target_column(df: pd.DataFrame) -> str:
    normalized = {col.lower(): col for col in df.columns}
    for candidate in TARGET_COLUMN_CANDIDATES:
        if candidate in normalized:
            return normalized[candidate]
    # fallback to last column
    return df.columns[-1]


def encode_dataframe(
    df: pd.DataFrame, target_column: str
) -> Tuple[pd.DataFrame, Dict[str, LabelEncoder], LabelEncoder]:
    feature_encoders: Dict[str, LabelEncoder] = {}

    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    for column in categorical_cols:
        if column == target_column:
            continue
        encoder = LabelEncoder()
        df[column] = encoder.fit_transform(df[column].astype(str))
        feature_encoders[column] = encoder

    target_encoder = LabelEncoder()
    df[target_column] = target_encoder.fit_transform(df[target_column].astype(str))

    return df, feature_encoders, target_encoder


def train() -> None:
    df = load_dataset()
    target_column = infer_target_column(df)

    # Basic cleaning: drop rows missing target, fill feature gaps
    df = df.dropna(subset=[target_column])
    feature_columns = [col for col in df.columns if col != target_column]
    if feature_columns:
        df[feature_columns] = df[feature_columns].fillna(method="ffill").fillna(method="bfill")

    df, feature_encoders, target_encoder = encode_dataframe(df, target_column)

    X = df.drop(columns=[target_column])
    y = df[target_column]
    feature_columns = X.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        eval_metric="mlogloss",
        n_jobs=-1,
        tree_method="hist",
    )
    model.fit(X_train, y_train)

    model_artifact = {"model": model, "feature_columns": feature_columns}
    encoder_artifact = {
        "target_column": target_column,
        "target_encoder": target_encoder,
        "feature_encoders": feature_encoders,
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_artifact, MODEL_PATH)
    joblib.dump(encoder_artifact, ENCODER_PATH)

    print(f"Training complete. Model saved to {MODEL_PATH}")
    print(f"Encoders saved to {ENCODER_PATH}")


if __name__ == "__main__":
    train()

