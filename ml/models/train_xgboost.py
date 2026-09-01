"""XGBoost model training module for revenue regression and success tier classification.

Trains both pre-release and early-signal models, logs detailed metrics,
and serializes artifacts to the model registry.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier, XGBRegressor

from ml.config import (
    MODEL_REGISTRY_DIR,
    PROCESSED_DATA_DIR,
    RANDOM_STATE,
    TEST_DATA_PATH,
    TRAIN_DATA_PATH,
)
from ml.evaluation.metrics import (
    calculate_classification_metrics,
    calculate_regression_metrics,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_datasets() -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Load train/test sets and feature manifest."""
    train_df = pd.read_parquet(TRAIN_DATA_PATH)
    test_df = pd.read_parquet(TEST_DATA_PATH)

    with open(PROCESSED_DATA_DIR / "feature_manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    return train_df, test_df, manifest


def train_xgb_regressor(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_estimators: int = 350,
    learning_rate: float = 0.04,
    max_depth: int = 5,
    subsample: float = 0.85,
    colsample_bytree: float = 0.85,
    reg_alpha: float = 0.5,
    reg_lambda: float = 1.0,
) -> XGBRegressor:
    """Instantiate and train an XGBRegressor."""
    model = XGBRegressor(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        reg_alpha=reg_alpha,
        reg_lambda=reg_lambda,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def train_xgb_classifier(
    X_train: pd.DataFrame,
    y_train_encoded: np.ndarray,
    n_estimators: int = 250,
    learning_rate: float = 0.05,
    max_depth: int = 4,
) -> XGBClassifier:
    """Instantiate and train a multi-class XGBClassifier."""
    # Compute class weights for imbalanced tiers
    classes, counts = np.unique(y_train_encoded, return_counts=True)
    total_samples = len(y_train_encoded)
    class_weights = {c: total_samples / (len(classes) * count) for c, count in zip(classes, counts)}
    sample_weights = np.array([class_weights[y] for y in y_train_encoded])

    model = XGBClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        objective="multi:softprob",
        num_class=len(classes),
        eval_metric="mlogloss",
    )
    model.fit(X_train, y_train_encoded, sample_weight=sample_weights)
    return model


def run_xgboost_pipeline() -> Dict[str, Any]:
    """Train pre-release regressor, early-signal regressor, and classifier."""
    train_df, test_df, manifest = load_datasets()

    pre_features: List[str] = manifest["pre_release_features"]
    early_features: List[str] = pre_features + manifest["early_signal_features"]
    reg_target: str = manifest["targets"]["regression_target_log"]
    cls_target: str = manifest["targets"]["classification_target"]

    MODEL_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Pre-Release XGBRegressor (Primary production model)
    logger.info("Training Pre-Release XGBRegressor (features=%d)...", len(pre_features))
    X_train_pre = train_df[pre_features].fillna(0)
    y_train_reg = train_df[reg_target]
    X_test_pre = test_df[pre_features].fillna(0)
    y_test_reg = test_df[reg_target]

    xgb_reg_pre = train_xgb_regressor(X_train_pre, y_train_reg)

    train_pred_pre = xgb_reg_pre.predict(X_train_pre)
    test_pred_pre = xgb_reg_pre.predict(X_test_pre)

    metrics_pre_train = calculate_regression_metrics(y_train_reg.values, train_pred_pre, prefix="train")
    metrics_pre_test = calculate_regression_metrics(y_test_reg.values, test_pred_pre, prefix="test")

    logger.info("Pre-Release Test R²: %.4f | RMSE: %.4f | MAE: %.4f | Pearson R: %.4f",
                metrics_pre_test["test_r2_log"], metrics_pre_test["test_rmse_log"],
                metrics_pre_test["test_mae_log"], metrics_pre_test["test_pearson_r"])

    # 2. Early-Signal XGBRegressor (Comparison / Leakage analysis model)
    logger.info("Training Early-Signal XGBRegressor (features=%d)...", len(early_features))
    X_train_early = train_df[early_features].fillna(0)
    X_test_early = test_df[early_features].fillna(0)

    xgb_reg_early = train_xgb_regressor(X_train_early, y_train_reg)

    test_pred_early = xgb_reg_early.predict(X_test_early)
    metrics_early_test = calculate_regression_metrics(y_test_reg.values, test_pred_early, prefix="test")

    logger.info("Early-Signal Test R²: %.4f | RMSE: %.4f | MAE: %.4f | Pearson R: %.4f",
                metrics_early_test["test_r2_log"], metrics_early_test["test_rmse_log"],
                metrics_early_test["test_mae_log"], metrics_early_test["test_pearson_r"])

    # 3. XGBClassifier for Success Tier
    logger.info("Training Pre-Release XGBClassifier for Success Tier...")
    label_encoder = LabelEncoder()
    tier_order = ["Flop", "Break-even", "Hit", "Blockbuster"]
    label_encoder.fit(tier_order)

    y_train_cls = train_df[cls_target].fillna("Flop")
    y_test_cls = test_df[cls_target].fillna("Flop")

    y_train_cls_enc = label_encoder.transform(y_train_cls)
    y_test_cls_enc = label_encoder.transform(y_test_cls)

    xgb_cls = train_xgb_classifier(X_train_pre, y_train_cls_enc)

    test_cls_pred_enc = xgb_cls.predict(X_test_pre)
    test_cls_pred = label_encoder.inverse_transform(test_cls_pred_enc)

    cls_metrics = calculate_classification_metrics(y_test_cls.values, test_cls_pred, labels=tier_order, prefix="test")
    logger.info("Success Tier Test Accuracy: %.4f | Macro F1: %.4f", cls_metrics["test_accuracy"], cls_metrics["test_macro_f1"])

    # Save artifacts
    artifacts = {
        "xgb_regressor_prerelease.joblib": {
            "model": xgb_reg_pre,
            "features": pre_features,
            "feature_type": "pre_release",
            "target": reg_target,
            "metrics": {"train": metrics_pre_train, "test": metrics_pre_test},
        },
        "xgb_regressor_earlysignal.joblib": {
            "model": xgb_reg_early,
            "features": early_features,
            "feature_type": "early_signal",
            "target": reg_target,
            "metrics": {"test": metrics_early_test},
        },
        "xgb_classifier_tier.joblib": {
            "model": xgb_cls,
            "label_encoder": label_encoder,
            "tier_labels": tier_order,
            "features": pre_features,
            "target": cls_target,
            "metrics": cls_metrics,
        },
    }

    for filename, payload in artifacts.items():
        joblib.dump(payload, MODEL_REGISTRY_DIR / filename)
        logger.info("Saved artifact %s", filename)

    return {
        "pre_release_regression": metrics_pre_test,
        "early_signal_regression": metrics_early_test,
        "tier_classification": cls_metrics,
    }


if __name__ == "__main__":
    run_xgboost_pipeline()
