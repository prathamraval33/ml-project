"""Machine Learning Inference Service for CineForecast.

Loads champion models, transforms raw movie parameters into feature vectors,
performs revenue regression and success tier classification, and calculates SHAP values.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

from backend.app.config import settings
from backend.app.schemas.predict import (
    PredictRequest,
    PredictResponse,
    ShapContribution,
    WhatIfRequest,
    WhatIfResponse,
)
from ml.evaluation.shap_explain import ShapExplainerService

logger = logging.getLogger(__name__)


class InferenceService:
    """Singleton service for live ML inference and explainability."""

    def __init__(self):
        self.model_dir = Path(settings.MODEL_REGISTRY_DIR)
        self.manifest_path = Path(settings.PROCESSED_DATA_DIR) / "feature_manifest.json"
        self.manifest: Dict[str, Any] = {}
        self.pre_features: List[str] = []
        self.genre_cols: List[str] = []
        self.regressor = None
        self.reg_features: List[str] = []
        self.classifier = None
        self.label_encoder = None
        self.tier_labels: List[str] = []
        self.shap_service: Optional[ShapExplainerService] = None

        self.load_models()

    def load_models(self) -> bool:
        """Attempt loading feature manifest and champion models from registry."""
        try:
            if self.manifest_path.exists():
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    self.manifest = json.load(f)
                self.pre_features = self.manifest.get("pre_release_features", [])
                self.genre_cols = self.manifest.get("genre_columns", [])

            # Load Champion Regressor
            reg_path = self.model_dir / "xgb_regressor_champion.joblib"
            if not reg_path.exists():
                reg_path = self.model_dir / "xgb_regressor_prerelease.joblib"

            if reg_path.exists():
                reg_art = joblib.load(reg_path)
                self.regressor = reg_art["model"]
                self.reg_features = reg_art["features"]
                self.shap_service = ShapExplainerService(model_path=reg_path)

            # Load Champion Classifier
            cls_path = self.model_dir / "xgb_classifier_champion.joblib"
            if not cls_path.exists():
                cls_path = self.model_dir / "xgb_classifier_tier.joblib"

            if cls_path.exists():
                cls_art = joblib.load(cls_path)
                self.classifier = cls_art["model"]
                self.label_encoder = cls_art["label_encoder"]
                self.tier_labels = cls_art["tier_labels"]

            if self.regressor is not None and self.classifier is not None:
                logger.info("InferenceService successfully initialized with %d features.", len(self.reg_features))
                return True
            else:
                logger.warning("InferenceService: Models not yet fully trained in registry.")
                return False
        except Exception as e:
            logger.warning("InferenceService initialization warning: %s", e)
            return False

    def _transform_payload_to_features(self, req: PredictRequest) -> Dict[str, Any]:
        """Convert a PredictRequest into the exact feature vector expected by models."""
        features: Dict[str, Any] = {}

        # 1. Budget & log budget
        budget = float(req.budget)
        features["budget"] = budget
        features["log_budget"] = float(np.log1p(budget))
        features["runtime"] = float(req.runtime)

        # 2. Counts
        features["cast_size"] = float(req.cast_size or 5)
        features["production_company_count"] = float(req.production_company_count or 1)
        features["production_country_count"] = float(req.production_country_count or 1)
        features["is_international_coproduction"] = 1.0 if features["production_country_count"] > 1 else 0.0
        features["is_franchise"] = float(req.is_franchise or 0)

        # 3. Release date parsing
        rel_date_str = req.release_date or "2026-07-15"
        try:
            rel_dt = datetime.strptime(rel_date_str, "%Y-%m-%d")
        except Exception:
            rel_dt = datetime(2026, 7, 15)

        features["release_year"] = float(rel_dt.year)
        features["release_month"] = float(rel_dt.month)
        features["release_quarter"] = float((rel_dt.month - 1) // 3 + 1)
        features["release_day_of_week"] = float(rel_dt.weekday())
        features["is_holiday_release"] = 1.0 if rel_dt.month in [6, 7, 11, 12] else 0.0

        # 4. Priors
        features["director_prior_avg_revenue"] = float(req.director_prior_avg_revenue or 0.0)
        features["director_prior_film_count"] = float(req.director_prior_film_count or 0.0)
        features["primary_production_company_prior_avg_revenue"] = float(
            req.primary_production_company_prior_avg_revenue or 0.0
        )
        features["primary_production_company_prior_film_count"] = float(
            req.primary_production_company_prior_film_count or 0.0
        )

        # 5. Multi-hot genres
        user_genres = [g.strip().lower() for g in (req.genres or ["Drama"])]
        for gcol in self.genre_cols:
            # gcol is e.g. "genre_science_fiction"
            norm_g = gcol.replace("genre_", "").replace("_", " ")
            features[gcol] = 1.0 if any(ug in norm_g or norm_g in ug for ug in user_genres) else 0.0

        # Ensure all required features are present
        for f in self.reg_features:
            if f not in features:
                features[f] = 0.0

        return features

    def predict(self, req: PredictRequest) -> PredictResponse:
        """Run end-to-end inference and SHAP decomposition."""
        if self.regressor is None or self.classifier is None:
            if not self.load_models():
                raise RuntimeError("ML models are not loaded. Please ensure models are trained and present in registry.")

        features = self._transform_payload_to_features(req)
        feature_df = pd.DataFrame([[features[f] for f in self.reg_features]], columns=self.reg_features)

        # 1. Regression (Revenue)
        pred_log_revenue = float(self.regressor.predict(feature_df)[0])
        pred_revenue = float(np.expm1(np.clip(pred_log_revenue, 0, 30)))
        pred_roi = float((pred_revenue - req.budget) / req.budget)

        # 2. Classification (Success Tier)
        proba = self.classifier.predict_proba(feature_df)[0]
        tier_idx = int(np.argmax(proba))
        pred_tier = self.label_encoder.inverse_transform([tier_idx])[0]

        tier_probs = {
            tier: round(float(p), 4)
            for tier, p in zip(self.label_encoder.classes_, proba)
        }

        # 3. SHAP Waterfall
        shap_res = self.shap_service.explain_single(features)
        pos_contribs = [ShapContribution(**c) for c in shap_res["top_positive"]]
        neg_contribs = [ShapContribution(**c) for c in shap_res["top_negative"]]
        all_contribs = [ShapContribution(**c) for c in shap_res["contributions"]]

        return PredictResponse(
            title=req.title or "Untitled Film",
            budget=req.budget,
            predicted_revenue=round(pred_revenue, 2),
            predicted_roi=round(pred_roi, 4),
            predicted_tier=pred_tier,
            confidence_tier_probabilities=tier_probs,
            base_value=shap_res["base_value_usd"],
            top_positive_factors=pos_contribs,
            top_negative_factors=neg_contribs,
            all_contributions=all_contribs,
        )

    def whatif_simulate(self, req: WhatIfRequest) -> WhatIfResponse:
        """Simulate the effect of parameter adjustments against baseline."""
        # 1. Establish baseline
        base = req.base_params or PredictRequest(
            title="Base Simulation",
            budget=50_000_000.0,
            runtime=115,
            genres=["Action", "Adventure"],
            release_date="2026-07-04",
        )

        base_res = self.predict(base)

        # 2. Apply adjustments
        mod_dict = base.model_dump()
        for k, v in req.adjustments.items():
            if k in mod_dict:
                mod_dict[k] = v

        mod_req = PredictRequest(**mod_dict)
        mod_res = self.predict(mod_req)

        # 3. Compute deltas
        rev_delta = mod_res.predicted_revenue - base_res.predicted_revenue
        rev_delta_pct = (rev_delta / base_res.predicted_revenue) * 100.0 if base_res.predicted_revenue > 0 else 0.0
        roi_delta = mod_res.predicted_roi - base_res.predicted_roi

        return WhatIfResponse(
            base_budget=base_res.budget,
            modified_budget=mod_res.budget,
            base_predicted_revenue=base_res.predicted_revenue,
            modified_predicted_revenue=mod_res.predicted_revenue,
            revenue_delta=round(rev_delta, 2),
            revenue_delta_percent=round(rev_delta_pct, 2),
            base_predicted_roi=base_res.predicted_roi,
            modified_predicted_roi=mod_res.predicted_roi,
            roi_delta=round(roi_delta, 4),
            base_predicted_tier=base_res.predicted_tier,
            modified_predicted_tier=mod_res.predicted_tier,
            tier_changed=(base_res.predicted_tier != mod_res.predicted_tier),
            modified_top_positive_factors=mod_res.top_positive_factors,
            modified_top_negative_factors=mod_res.top_negative_factors,
        )


inference_service = InferenceService()
