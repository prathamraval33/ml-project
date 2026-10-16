"""CatBoost benchmark model training module.

Trains CatBoostRegressor and CatBoostClassifier to benchmark gradient boosting
performance against XGBoost on the CineForecast dataset.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier, CatBoostRegressor
from sklearn.preprocessing import LabelEncoder

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


def run_catboost_pipeline() -> Dict[str, Any]:
    """Train CatBoost Regressor and Classifier on pre-release features."""
    train_df, test_df, manifest = load_datasets()

    pre_features: List[str] = manifest["pre_release_features"]
    reg_target: str = manifest["targets"]["regression_target_log"]
    cls_target: str = manifest["targets"]["classification_target"]

    X_train = train_df[pre_features].fillna(0)
    y_train_reg = train_df[reg_target]
    X_test = test_df[pre_features].fillna(0)
    y_test_reg = test_df[reg_target]

    logger.info("Training CatBoostRegressor (features=%d)...", len(pre_features))
    cb_reg = CatBoostRegressor(
        iterations=400,
        learning_rate=0.04,
        depth=6,
        random_seed=RANDOM_STATE,
        verbose=0,
    )
    cb_reg.fit(X_train, y_train_reg)

    test_preds = cb_reg.predict(X_test)
    cb_reg_metrics = calculate_regression_metrics(y_test_reg.values, test_preds, prefix="test")

    logger.info("CatBoost Test R²: %.4f | RMSE: %.4f | MAE: %.4f",
                cb_reg_metrics["test_r2_log"], cb_reg_metrics["test_rmse_log"], cb_reg_metrics["test_mae_log"])

    # CatBoost Classifier
    logger.info("Training CatBoostClassifier for Success Tier...")
    tier_order = ["Flop", "Break-even", "Hit", "Blockbuster"]
    label_encoder = LabelEncoder()
    label_encoder.fit(tier_order)

    y_train_cls = train_df[cls_target].fillna("Flop")
    y_test_cls = test_df[cls_target].fillna("Flop")

    y_train_cls_enc = label_encoder.transform(y_train_cls)
    y_test_cls_enc = label_encoder.transform(y_test_cls)

    cb_cls = CatBoostClassifier(
        iterations=300,
        learning_rate=0.05,
        depth=5,
        random_seed=RANDOM_STATE,
        loss_function="MultiClass",
        verbose=0,
    )
    cb_cls.fit(X_train, y_train_cls_enc)

    test_cls_preds_enc = cb_cls.predict(X_test).ravel()
    test_cls_preds = label_encoder.inverse_transform(np.rint(test_cls_preds_enc).astype(int))

    cb_cls_metrics = calculate_classification_metrics(y_test_cls.values, test_cls_preds, labels=tier_order, prefix="test")
    logger.info("CatBoost Tier Accuracy: %.4f | Macro F1: %.4f", cb_cls_metrics["test_accuracy"], cb_cls_metrics["test_macro_f1"])

    MODEL_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "regressor": cb_reg,
            "classifier": cb_cls,
            "features": pre_features,
            "reg_metrics": cb_reg_metrics,
            "cls_metrics": cb_cls_metrics,
        },
        MODEL_REGISTRY_DIR / "catboost_benchmark.joblib",
    )

    return {"regression": cb_reg_metrics, "classification": cb_cls_metrics}


if __name__ == "__main__":
    run_catboost_pipeline()
