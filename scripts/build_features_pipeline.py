"""Pipeline script to execute Phase 3 Feature Engineering.

Performs:
1. Loads interim deduplicated dataset.
2. Filters to training-eligible records.
3. Chronological train/test split at TEST_SPLIT_YEAR (2023).
4. Fits and transforms features with zero leakage.
5. Saves train.parquet, test.parquet, and feature_manifest.json.
"""

import sys
import logging
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.config import INTERIM_DATA_PATH, TEST_SPLIT_YEAR
from ml.features.build_features import engineer_features, save_processed_datasets

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Phase 3: Feature Engineering Pipeline...")
    df = pd.read_parquet(INTERIM_DATA_PATH)
    logger.info("Loaded interim data: %d rows", len(df))

    # Restrict to records eligible for training (budget>0, revenue>0, valid years and runtime)
    eligible = df[df["is_usable_for_training"]].copy()
    logger.info("Training eligible rows: %d", len(eligible))

    # Chronological Split (Train: release_year < TEST_SPLIT_YEAR, Test: release_year >= TEST_SPLIT_YEAR)
    train_raw = eligible[eligible["release_year"] < TEST_SPLIT_YEAR].copy()
    test_raw = eligible[eligible["release_year"] >= TEST_SPLIT_YEAR].copy()

    logger.info(
        "Chronological Split (Cutoff %d): Train = %d rows (years %d–%d), Test = %d rows (years %d–%d)",
        TEST_SPLIT_YEAR,
        len(train_raw),
        train_raw["release_year"].min(),
        train_raw["release_year"].max(),
        len(test_raw),
        test_raw["release_year"].min(),
        test_raw["release_year"].max(),
    )

    # Feature engineering
    train_proc, test_proc, manifest = engineer_features(train_raw, test_raw)

    # Save outputs
    save_processed_datasets(train_proc, test_proc, manifest)

    logger.info("Pre-release feature count: %d", len(manifest["pre_release_features"]))
    logger.info("Early-signal feature count: %d", len(manifest["early_signal_features"]))
    logger.info("Phase 3 Feature Engineering complete!")


if __name__ == "__main__":
    main()
