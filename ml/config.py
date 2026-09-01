"""Central configuration for CineForecast Machine Learning pipeline.

Defines directory paths, data cleaning rules, feature engineering parameters,
and modeling hyperparameters to avoid magic numbers across the codebase.
"""

from pathlib import Path
from typing import List

# Project Root and Data Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "dataset_1_collected_data.csv"
INTERIM_DATA_DIR = DATA_DIR / "interim"
INTERIM_DATA_PATH = INTERIM_DATA_DIR / "deduplicated_parsed.parquet"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
TRAIN_DATA_PATH = PROCESSED_DATA_DIR / "train.parquet"
TEST_DATA_PATH = PROCESSED_DATA_DIR / "test.parquet"
FEATURE_MANIFEST_PATH = PROCESSED_DATA_DIR / "feature_manifest.json"

# Models and Artifacts
MODEL_REGISTRY_DIR = PROJECT_ROOT / "ml" / "models" / "registry"
SHAP_CACHE_DIR = MODEL_REGISTRY_DIR / "shap_cache"

# Data Cleaning Thresholds (Section 3.2 & 3.3)
MIN_RELEASE_YEAR: int = 1990
MAX_RELEASE_YEAR: int = 2026  # Snapshot cutoff to exclude future releases (e.g. up to 2031)
MIN_RUNTIME_MINUTES: int = 40  # Exclude zero or extreme sub-feature film runtime
MAX_RUNTIME_MINUTES: int = 360

# Train/Test Split (Temporal Chronological Cutoff)
# Releases from 2023 onwards held out as test set
TEST_SPLIT_YEAR: int = 2023

# Reproducibility
RANDOM_STATE: int = 42

# List column fields to parse safely with ast.literal_eval
LIST_COLUMNS: List[str] = [
    "genres",
    "production_companies",
    "production_countries",
    "cast",
]

# Success Tier Boundaries (Derived from ROI = (revenue - budget) / budget)
ROI_TIERS = {
    "Flop": (-float("inf"), 0.0),
    "Break-even": (0.0, 1.0),
    "Hit": (1.0, 3.0),
    "Blockbuster": (3.0, float("inf")),
}

# Holiday / Peak Release Months (Summer blockbusters + Year-end holidays)
HOLIDAY_MONTHS: List[int] = [6, 7, 11, 12]

# IMDB Weighted Rating (Bayesian adjustment) baseline
IMDB_MIN_VOTES_QUANTILE: float = 0.65  # m threshold
