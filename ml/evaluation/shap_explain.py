"""SHAP Explainability module for CineForecast.

Computes TreeExplainer SHAP values, global feature importances,
and per-movie SHAP waterfall contributions cached for the API and dashboard.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
import shap

from ml.config import (
    MODEL_REGISTRY_DIR,
    PROCESSED_DATA_DIR,
    SHAP_CACHE_DIR,
    TEST_DATA_PATH,
    TRAIN_DATA_PATH,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class ShapExplainerService:
    """Wrapper for SHAP TreeExplainer on CineForecast models."""

    def __init__(self, model_path: Optional[Path] = None):
        """Load trained champion model and initialize TreeExplainer."""
        if model_path is None:
            # Try champion first, fallback to prerelease
            champion_path = MODEL_REGISTRY_DIR / "xgb_regressor_champion.joblib"
            prerelease_path = MODEL_REGISTRY_DIR / "xgb_regressor_prerelease.joblib"
            model_path = champion_path if champion_path.exists() else prerelease_path

        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found at {model_path}. Train model first.")

        artifact = joblib.load(model_path)
        self.model = artifact["model"]
        self.features: List[str] = artifact["features"]
        self.explainer = shap.TreeExplainer(self.model)
        exp_val = self.explainer.expected_value
        if isinstance(exp_val, (list, np.ndarray)):
            self.expected_value = float(exp_val[0])
        else:
            self.expected_value = float(exp_val)

    def explain_single(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Compute SHAP waterfall breakdown for a single movie's feature dict."""
        # Align features
        row_values = [float(feature_dict.get(col, 0.0) or 0.0) for col in self.features]
        row_df = pd.DataFrame([row_values], columns=self.features)

        shap_values = self.explainer.shap_values(row_df)[0]
        predicted_log_revenue = float(self.model.predict(row_df)[0])
        predicted_usd = float(np.expm1(np.clip(predicted_log_revenue, 0, 30)))

        # Format waterfall breakdown sorted by absolute contribution
        contributions = []
        for feat_name, feat_val, shap_val in zip(self.features, row_values, shap_values):
            contributions.append({
                "feature": feat_name,
                "value": feat_val,
                "shap_value": round(float(shap_val), 4),
                "abs_shap": round(float(abs(shap_val)), 4),
            })

        contributions.sort(key=lambda x: x["abs_shap"], reverse=True)

        return {
            "base_value_log": round(self.expected_value, 4),
            "base_value_usd": round(float(np.expm1(self.expected_value)), 2),
            "predicted_log_revenue": round(predicted_log_revenue, 4),
            "predicted_revenue_usd": round(predicted_usd, 2),
            "contributions": contributions,
            "top_positive": [c for c in contributions if c["shap_value"] > 0][:5],
            "top_negative": [c for c in contributions if c["shap_value"] < 0][:5],
        }

    def compute_and_cache_test_set_explanations(self, test_df_path: Path = TEST_DATA_PATH) -> Dict[str, Any]:
        """Pre-compute and cache SHAP waterfall explanations for all test set films."""
        test_df = pd.read_parquet(test_df_path)
        SHAP_CACHE_DIR.mkdir(parents=True, exist_ok=True)

        logger.info("Computing global SHAP summary on test set (%d movies)...", len(test_df))
        X_test = test_df[self.features].fillna(0)
        shap_values = self.explainer.shap_values(X_test)

        mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
        feature_importance = [
            {
                "feature": feat,
                "mean_abs_shap": round(float(imp), 4),
                "rank": idx + 1,
            }
            for idx, (imp, feat) in enumerate(
                sorted(zip(mean_abs_shap, self.features), key=lambda x: x[0], reverse=True)
            )
        ]

        global_summary = {
            "base_value_log": round(self.expected_value, 4),
            "feature_importances": feature_importance,
            "sample_size": len(test_df),
        }

        global_summary_path = MODEL_REGISTRY_DIR / "global_shap_summary.json"
        with open(global_summary_path, "w", encoding="utf-8") as f:
            json.dump(global_summary, f, indent=2)
        logger.info("Saved global SHAP summary to %s", global_summary_path)

        logger.info("Caching per-movie SHAP waterfalls to %s...", SHAP_CACHE_DIR)
        cached_count = 0
        for idx, row in test_df.iterrows():
            movie_id = int(row.get("id", idx))
            feature_dict = row[self.features].to_dict()
            explanation = self.explain_single(feature_dict)
            explanation["movie_id"] = movie_id
            explanation["title"] = str(row.get("title", f"Movie {movie_id}"))

            cache_file = SHAP_CACHE_DIR / f"{movie_id}.json"
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(explanation, f, indent=2)
            cached_count += 1

        logger.info("Cached %d per-movie SHAP explanation files successfully.", cached_count)
        return global_summary


def run_shap_pipeline() -> Dict[str, Any]:
    """Execute SHAP explanation generation and caching."""
    service = ShapExplainerService()
    summary = service.compute_and_cache_test_set_explanations()
    return summary


if __name__ == "__main__":
    run_shap_pipeline()
