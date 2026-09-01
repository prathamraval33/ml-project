"""Hyperparameter optimization module using Optuna.

Conducts Bayesian hyperparameter search using time-series chronological validation
to tune the champion XGBoost Regressor and Classifier models.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import optuna
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
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

optuna.logging.set_verbosity(optuna.logging.WARNING)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_datasets() -> Tuple[pd.DataFrame, pd.DataFrame, List[str], str, str]:
    """Load train/test sets and feature definitions."""
    train_df = pd.read_parquet(TRAIN_DATA_PATH)
    test_df = pd.read_parquet(TEST_DATA_PATH)

    with open(PROCESSED_DATA_DIR / "feature_manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    pre_features = manifest["pre_release_features"]
    reg_target = manifest["targets"]["regression_target_log"]
    cls_target = manifest["targets"]["classification_target"]

    return train_df, test_df, pre_features, reg_target, cls_target


def optimize_xgb_regressor(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_trials: int = 30,
) -> Tuple[Dict[str, Any], XGBRegressor]:
    """Tune XGBRegressor hyperparameters with Optuna using TimeSeriesSplit cross-validation."""
    tscv = TimeSeriesSplit(n_splits=3)

    def objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 150, 500, step=50),
            "max_depth": trial.suggest_int("max_depth", 3, 7),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.12, log=True),
            "subsample": trial.suggest_float("subsample", 0.65, 0.95),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.65, 0.95),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-3, 5.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-2, 10.0, log=True),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 8),
            "random_state": RANDOM_STATE,
            "n_jobs": -1,
        }

        cv_rmses = []
        for train_idx, val_idx in tscv.split(X_train):
            X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

            model = XGBRegressor(**params)
            model.fit(X_tr, y_tr)
            preds = model.predict(X_val)
            rmse = np.sqrt(np.mean((y_val - preds) ** 2))
            cv_rmses.append(rmse)

        return float(np.mean(cv_rmses))

    logger.info("Starting Optuna search for XGBRegressor (%d trials)...", n_trials)
    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE))
    study.optimize(objective, n_trials=n_trials)

    best_params = study.best_params
    best_params["random_state"] = RANDOM_STATE
    best_params["n_jobs"] = -1
    logger.info("Best Regressor Params: %s (CV RMSE: %.4f)", best_params, study.best_value)

    champion_regressor = XGBRegressor(**best_params)
    champion_regressor.fit(X_train, y_train)

    return best_params, champion_regressor


def optimize_xgb_classifier(
    X_train: pd.DataFrame,
    y_train_encoded: np.ndarray,
    n_trials: int = 25,
) -> Tuple[Dict[str, Any], XGBClassifier]:
    """Tune XGBClassifier hyperparameters for success tier."""
    classes, counts = np.unique(y_train_encoded, return_counts=True)
    total = len(y_train_encoded)
    class_weights = {c: total / (len(classes) * count) for c, count in zip(classes, counts)}
    sample_weights = np.array([class_weights[y] for y in y_train_encoded])

    tscv = TimeSeriesSplit(n_splits=3)

    def objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 150, 400, step=50),
            "max_depth": trial.suggest_int("max_depth", 3, 6),
            "learning_rate": trial.suggest_float("learning_rate", 0.02, 0.15, log=True),
            "subsample": trial.suggest_float("subsample", 0.7, 0.95),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.7, 0.95),
            "random_state": RANDOM_STATE,
            "n_jobs": -1,
            "objective": "multi:softprob",
            "num_class": len(classes),
            "eval_metric": "mlogloss",
        }

        cv_losses = []
        for train_idx, val_idx in tscv.split(X_train):
            X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_val = y_train_encoded[train_idx], y_train_encoded[val_idx]
            sw_tr = sample_weights[train_idx]

            model = XGBClassifier(**params)
            model.fit(X_tr, y_tr, sample_weight=sw_tr)
            preds_proba = model.predict_proba(X_val)
            # mlogloss
            eps = 1e-15
            preds_proba = np.clip(preds_proba, eps, 1 - eps)
            loss = -np.mean(np.log(preds_proba[np.arange(len(y_val)), y_val]))
            cv_losses.append(loss)

        return float(np.mean(cv_losses))

    logger.info("Starting Optuna search for XGBClassifier (%d trials)...", n_trials)
    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE))
    study.optimize(objective, n_trials=n_trials)

    best_params = study.best_params
    best_params["random_state"] = RANDOM_STATE
    best_params["n_jobs"] = -1
    best_params["objective"] = "multi:softprob"
    best_params["num_class"] = len(classes)
    best_params["eval_metric"] = "mlogloss"

    champion_classifier = XGBClassifier(**best_params)
    champion_classifier.fit(X_train, y_train_encoded, sample_weight=sample_weights)

    return best_params, champion_classifier


def run_tuning_pipeline() -> Dict[str, Any]:
    """Execute complete hyperparameter tuning and save champion models."""
    train_df, test_df, pre_features, reg_target, cls_target = load_datasets()

    X_train = train_df[pre_features].fillna(0)
    y_train_reg = train_df[reg_target]
    X_test = test_df[pre_features].fillna(0)
    y_test_reg = test_df[reg_target]

    # 1. Regressor Tuning
    best_reg_params, champion_regressor = optimize_xgb_regressor(X_train, y_train_reg, n_trials=25)
    test_reg_preds = champion_regressor.predict(X_test)
    champion_reg_metrics = calculate_regression_metrics(y_test_reg.values, test_reg_preds, prefix="test")

    logger.info("Tuned Champion Regressor Test R²: %.4f | RMSE: %.4f | MAE: %.4f | Pearson R: %.4f",
                champion_reg_metrics["test_r2_log"], champion_reg_metrics["test_rmse_log"],
                champion_reg_metrics["test_mae_log"], champion_reg_metrics["test_pearson_r"])

    # 2. Classifier Tuning
    tier_order = ["Flop", "Break-even", "Hit", "Blockbuster"]
    label_encoder = LabelEncoder()
    label_encoder.fit(tier_order)

    y_train_cls = train_df[cls_target].fillna("Flop")
    y_test_cls = test_df[cls_target].fillna("Flop")
    y_train_cls_enc = label_encoder.transform(y_train_cls)

    best_cls_params, champion_classifier = optimize_xgb_classifier(X_train, y_train_cls_enc, n_trials=20)
    test_cls_preds_enc = champion_classifier.predict(X_test)
    test_cls_preds = label_encoder.inverse_transform(test_cls_preds_enc)
    champion_cls_metrics = calculate_classification_metrics(y_test_cls.values, test_cls_preds, labels=tier_order, prefix="test")

    logger.info("Tuned Champion Classifier Test Accuracy: %.4f | Macro F1: %.4f",
                champion_cls_metrics["test_accuracy"], champion_cls_metrics["test_macro_f1"])

    MODEL_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

    # Save champion artifacts
    reg_artifact_path = MODEL_REGISTRY_DIR / "xgb_regressor_champion.joblib"
    joblib.dump(
        {
            "model": champion_regressor,
            "params": best_reg_params,
            "features": pre_features,
            "target": reg_target,
            "metrics": champion_reg_metrics,
        },
        reg_artifact_path,
    )

    cls_artifact_path = MODEL_REGISTRY_DIR / "xgb_classifier_champion.joblib"
    joblib.dump(
        {
            "model": champion_classifier,
            "params": best_cls_params,
            "label_encoder": label_encoder,
            "tier_labels": tier_order,
            "features": pre_features,
            "target": cls_target,
            "metrics": champion_cls_metrics,
        },
        cls_artifact_path,
    )

    logger.info("Saved champion models to %s and %s", reg_artifact_path, cls_artifact_path)

    return {
        "regressor_params": best_reg_params,
        "regressor_metrics": champion_reg_metrics,
        "classifier_params": best_cls_params,
        "classifier_metrics": champion_cls_metrics,
    }


if __name__ == "__main__":
    run_tuning_pipeline()
