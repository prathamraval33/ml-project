"""End-to-End CineForecast ML Pipeline Orchestrator.

Sequentially executes:
1. Data cleaning & parsing (Phase 1)
2. Feature engineering & temporal train/test split (Phase 3)
3. Baseline Ridge model training (Phase 4)
4. Primary XGBoost models training (Phase 4)
5. CatBoost benchmark model training (Phase 4)
6. Leakage ablation study (Phase 4)
7. Hyperparameter tuning via Optuna (Phase 5)
8. SHAP global & per-movie explanation caching (Phase 5)
"""

import logging
import time

from ml.data.clean import run_cleaning_pipeline
from ml.evaluation.ablation_study import run_leakage_ablation_study
from ml.evaluation.shap_explain import run_shap_pipeline
from ml.features.build_features import run_feature_engineering_pipeline
from ml.models.train_baseline import run_baseline_training
from ml.models.train_catboost import run_catboost_pipeline
from ml.models.train_xgboost import run_xgboost_pipeline
from ml.models.tune_optuna import run_tuning_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ml_pipeline")


def run_full_ml_pipeline() -> None:
    """Execute complete ML pipeline from raw CSV to cached SHAP explanations."""
    start_time = time.time()
    logger.info("==================================================")
    logger.info("🎬 STARTING CINEFORECAST FULL ML PIPELINE 🎬")
    logger.info("==================================================")

    logger.info("--- [Step 1/8] Data Cleaning & Parsing ---")
    run_cleaning_pipeline()

    logger.info("--- [Step 2/8] Leakage-Safe Feature Engineering ---")
    run_feature_engineering_pipeline()

    logger.info("--- [Step 3/8] Baseline Ridge Regressor ---")
    run_baseline_training()

    logger.info("--- [Step 4/8] XGBoost Regressor & Classifier ---")
    run_xgboost_pipeline()

    logger.info("--- [Step 5/8] CatBoost Benchmark Models ---")
    run_catboost_pipeline()

    logger.info("--- [Step 6/8] Leakage Ablation Study ---")
    run_leakage_ablation_study()

    logger.info("--- [Step 7/8] Optuna Hyperparameter Tuning ---")
    run_tuning_pipeline()

    logger.info("--- [Step 8/8] SHAP Explanations & Cache Generation ---")
    run_shap_pipeline()

    elapsed = time.time() - start_time
    logger.info("==================================================")
    logger.info("✅ CINEFORECAST ML PIPELINE COMPLETE in %.2f seconds", elapsed)
    logger.info("==================================================")


if __name__ == "__main__":
    run_full_ml_pipeline()
