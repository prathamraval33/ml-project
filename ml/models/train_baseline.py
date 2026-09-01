"""Baseline model training: Ridge and Linear Regression on log revenue."""

import json
import logging
from pathlib import Path
from typing import Dict, Tuple, Any

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from ml.config import (
    MODEL_REGISTRY_DIR,
    PROCESSED_DATA_DIR,
    RANDOM_STATE,
    TEST_DATA_PATH,
    TRAIN_DATA_PATH,
)
from ml.evaluation.metrics import calculate_regression_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_data(
    train_path: Path = TRAIN_DATA_PATH,
    test_path: Path = TEST_DATA_PATH,
    manifest_path: Path = PROCESSED_DATA_DIR / "feature_manifest.json",
) -> Tuple[pd.DataFrame, pd.DataFrame, list, str]:
    """Load train/test parquet files and feature manifest."""
    train_df = pd.read_parquet(train_path)
    test_df = pd.read_parquet(test_path)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    pre_release_features = manifest["pre_release_features"]
    target_col = manifest["targets"]["regression_target_log"]
    return train_df, test_df, pre_release_features, target_col


def train_baseline_regressor(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    alpha: float = 1.0,
) -> Pipeline:
    """Train Ridge regression baseline inside a standard scaling pipeline."""
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("regressor", Ridge(alpha=alpha, random_state=RANDOM_STATE)),
        ]
    )
    pipeline.fit(X_train, y_train)
    return pipeline


def run_baseline_training() -> Dict[str, Any]:
    """Execute baseline model training and evaluation."""
    logger.info("Loading processed datasets for baseline training...")
    train_df, test_df, features, target_col = load_data()

    X_train = train_df[features].fillna(0)
    y_train = train_df[target_col]
    X_test = test_df[features].fillna(0)
    y_test = test_df[target_col]

    logger.info("Fitting Baseline Ridge Regressor on %d training rows (features=%d)...", len(X_train), len(features))
    model = train_baseline_regressor(X_train, y_train)

    train_preds = model.predict(X_train)
    test_preds = model.predict(X_test)

    train_metrics = calculate_regression_metrics(y_train.values, train_preds, prefix="train")
    test_metrics = calculate_regression_metrics(y_test.values, test_preds, prefix="test")

    logger.info("Baseline Train R²: %.4f | RMSE: %.4f", train_metrics["train_r2_log"], train_metrics["train_rmse_log"])
    logger.info("Baseline Test R²:  %.4f | RMSE: %.4f | MAE: %.4f", test_metrics["test_r2_log"], test_metrics["test_rmse_log"], test_metrics["test_mae_log"])

    MODEL_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_REGISTRY_DIR / "baseline_ridge.joblib"
    joblib.dump(
        {
            "model": model,
            "features": features,
            "target": target_col,
            "train_metrics": train_metrics,
            "test_metrics": test_metrics,
        },
        model_path,
    )
    logger.info("Saved baseline model to %s", model_path)

    return {"train_metrics": train_metrics, "test_metrics": test_metrics, "model_path": str(model_path)}


if __name__ == "__main__":
    run_baseline_training()
