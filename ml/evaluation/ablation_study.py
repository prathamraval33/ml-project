"""Leakage Ablation Study module.

Compares model performance with Pre-Release features (budget, genre, timing, priors)
versus Early-Signal features (including post-release TMDB popularity, vote count, vote average)
to quantitatively measure and document the target leakage / hindsight signal inflation effect.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from catboost import CatBoostRegressor

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


def run_leakage_ablation_study() -> Dict[str, Any]:
    """Execute ablation experiments comparing Pre-Release vs Early-Signal models."""
    train_df = pd.read_parquet(TRAIN_DATA_PATH)
    test_df = pd.read_parquet(TEST_DATA_PATH)

    with open(PROCESSED_DATA_DIR / "feature_manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    pre_features = manifest["pre_release_features"]
    early_features = pre_features + manifest["early_signal_features"]
    target_col = manifest["targets"]["regression_target_log"]

    y_train = train_df[target_col].values
    y_test = test_df[target_col].values

    results = []

    # 1. Baseline Ridge Regressor
    scaler_pre = StandardScaler()
    X_train_pre_scaled = scaler_pre.fit_transform(train_df[pre_features].fillna(0))
    X_test_pre_scaled = scaler_pre.transform(test_df[pre_features].fillna(0))

    ridge_pre = Ridge(alpha=1.0, random_state=RANDOM_STATE).fit(X_train_pre_scaled, y_train)
    m_ridge_pre = calculate_regression_metrics(y_test, ridge_pre.predict(X_test_pre_scaled))
    results.append({
        "model": "Ridge Regression",
        "feature_set": "Pre-Release (Clean)",
        "features_count": len(pre_features),
        "r2_log": m_ridge_pre["r2_log"],
        "rmse_log": m_ridge_pre["rmse_log"],
        "mae_log": m_ridge_pre["mae_log"],
        "pearson_r": m_ridge_pre["pearson_r"],
        "mdape_percent": m_ridge_pre["mdape_percent"],
    })

    scaler_early = StandardScaler()
    X_train_early_scaled = scaler_early.fit_transform(train_df[early_features].fillna(0))
    X_test_early_scaled = scaler_early.transform(test_df[early_features].fillna(0))

    ridge_early = Ridge(alpha=1.0, random_state=RANDOM_STATE).fit(X_train_early_scaled, y_train)
    m_ridge_early = calculate_regression_metrics(y_test, ridge_early.predict(X_test_early_scaled))
    results.append({
        "model": "Ridge Regression",
        "feature_set": "Early-Signal (+Popularity/Votes)",
        "features_count": len(early_features),
        "r2_log": m_ridge_early["r2_log"],
        "rmse_log": m_ridge_early["rmse_log"],
        "mae_log": m_ridge_early["mae_log"],
        "pearson_r": m_ridge_early["pearson_r"],
        "mdape_percent": m_ridge_early["mdape_percent"],
    })

    # 2. XGBoost Regressor
    xgb_pre = XGBRegressor(n_estimators=350, learning_rate=0.04, max_depth=5, random_state=RANDOM_STATE, n_jobs=-1)
    xgb_pre.fit(train_df[pre_features].fillna(0), y_train)
    m_xgb_pre = calculate_regression_metrics(y_test, xgb_pre.predict(test_df[pre_features].fillna(0)))
    results.append({
        "model": "XGBoost",
        "feature_set": "Pre-Release (Clean)",
        "features_count": len(pre_features),
        "r2_log": m_xgb_pre["r2_log"],
        "rmse_log": m_xgb_pre["rmse_log"],
        "mae_log": m_xgb_pre["mae_log"],
        "pearson_r": m_xgb_pre["pearson_r"],
        "mdape_percent": m_xgb_pre["mdape_percent"],
    })

    xgb_early = XGBRegressor(n_estimators=350, learning_rate=0.04, max_depth=5, random_state=RANDOM_STATE, n_jobs=-1)
    xgb_early.fit(train_df[early_features].fillna(0), y_train)
    m_xgb_early = calculate_regression_metrics(y_test, xgb_early.predict(test_df[early_features].fillna(0)))
    results.append({
        "model": "XGBoost",
        "feature_set": "Early-Signal (+Popularity/Votes)",
        "features_count": len(early_features),
        "r2_log": m_xgb_early["r2_log"],
        "rmse_log": m_xgb_early["rmse_log"],
        "mae_log": m_xgb_early["mae_log"],
        "pearson_r": m_xgb_early["pearson_r"],
        "mdape_percent": m_xgb_early["mdape_percent"],
    })

    # 3. CatBoost Regressor
    cb_pre = CatBoostRegressor(iterations=400, learning_rate=0.04, depth=6, random_seed=RANDOM_STATE, verbose=0)
    cb_pre.fit(train_df[pre_features].fillna(0), y_train)
    m_cb_pre = calculate_regression_metrics(y_test, cb_pre.predict(test_df[pre_features].fillna(0)))
    results.append({
        "model": "CatBoost",
        "feature_set": "Pre-Release (Clean)",
        "features_count": len(pre_features),
        "r2_log": m_cb_pre["r2_log"],
        "rmse_log": m_cb_pre["rmse_log"],
        "mae_log": m_cb_pre["mae_log"],
        "pearson_r": m_cb_pre["pearson_r"],
        "mdape_percent": m_cb_pre["mdape_percent"],
    })

    cb_early = CatBoostRegressor(iterations=400, learning_rate=0.04, depth=6, random_seed=RANDOM_STATE, verbose=0)
    cb_early.fit(train_df[early_features].fillna(0), y_train)
    m_cb_early = calculate_regression_metrics(y_test, cb_early.predict(test_df[early_features].fillna(0)))
    results.append({
        "model": "CatBoost",
        "feature_set": "Early-Signal (+Popularity/Votes)",
        "features_count": len(early_features),
        "r2_log": m_cb_early["r2_log"],
        "rmse_log": m_cb_early["rmse_log"],
        "mae_log": m_cb_early["mae_log"],
        "pearson_r": m_cb_early["pearson_r"],
        "mdape_percent": m_cb_early["mdape_percent"],
    })

    results_df = pd.DataFrame(results)
    logger.info("\n=== LEAKAGE ABLATION STUDY RESULTS ===\n%s", results_df.to_string(index=False))

    output_path = MODEL_REGISTRY_DIR / "leakage_ablation_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info("Saved ablation report to %s", output_path)
    return {"results": results}


if __name__ == "__main__":
    run_leakage_ablation_study()
