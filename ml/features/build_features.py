"""Full feature engineering pipeline for CineForecast.

Constructs both pre-release and early-signal feature matrices, applies
multi-hot genre encoding, leakage-safe director/studio rolling aggregates,
Bayesian vote adjustments, and logs all feature mappings to feature_manifest.json.
"""

import json
import logging
import re
from pathlib import Path
from typing import Tuple, Dict, Any, List
import pandas as pd
import numpy as np

from ml.config import (
    HOLIDAY_MONTHS,
    IMDB_MIN_VOTES_QUANTILE,
    FEATURE_MANIFEST_PATH,
    PROCESSED_DATA_DIR,
    TRAIN_DATA_PATH,
    TEST_DATA_PATH,
    TEST_SPLIT_YEAR,
)
from ml.features.encoders import MultiHotGenreEncoder
from ml.features.leakage_safe_aggregates import LeakageSafeHistoricalAggregator

logger = logging.getLogger(__name__)

# Regex for franchise / sequel title detection
SEQUEL_REGEX = re.compile(
    r"\b(part\s*\d+|volume\s*\d+|\b\d+\b|ii|iii|iv|v|vi|vii|viii|ix|x|chapter|returns|rises|reloaded|revolution|resurrection|awakens)\b|:",
    re.IGNORECASE,
)


def detect_franchise(title: str) -> int:
    """Detect if title follows typical sequel or franchise naming conventions."""
    if not isinstance(title, str):
        return 0
    return 1 if SEQUEL_REGEX.search(title) else 0


def assign_success_tier(roi: float) -> str:
    """Assign success tier based on financial return on investment."""
    if pd.isna(roi):
        return "Unknown"
    if roi < 0.0:
        return "Flop"
    elif roi < 1.0:
        return "Break-even"
    elif roi < 3.0:
        return "Hit"
    else:
        return "Blockbuster"


def compute_bayesian_rating(
    df: pd.DataFrame,
    global_mean_rating: float,
    min_vote_threshold: float,
) -> pd.Series:
    """Compute IMDB-style Bayesian weighted rating to prevent low-count vote bias."""
    v = df["vote_count"].fillna(0)
    r = df["vote_average"].fillna(global_mean_rating)
    m = min_vote_threshold
    c = global_mean_rating
    return (v / (v + m)) * r + (m / (v + m)) * c


def engineer_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Build feature sets for training and testing splits without data leakage.

    Args:
        train_df: Cleaned training DataFrame.
        test_df: Cleaned test DataFrame.

    Returns:
        Tuple of (train_processed_df, test_processed_df, feature_manifest_dict).
    """
    logger.info("Building features on Train (%d rows) and Test (%d rows)", len(train_df), len(test_df))

    # Base transforms on train and test
    def base_transforms(df: pd.DataFrame) -> pd.DataFrame:
        d = df.copy()
        d["is_franchise"] = d["title"].apply(detect_franchise)
        d["is_international_coproduction"] = (d["production_country_count"] > 1).astype(int)
        d["is_holiday_release"] = d["release_month"].isin(HOLIDAY_MONTHS).astype(int)

        # Financial transformations
        d["log_budget"] = np.log1p(np.maximum(d["budget"], 0))
        if "revenue" in d.columns:
            d["log_revenue"] = np.log1p(np.maximum(d["revenue"], 0))
            d["roi"] = (d["revenue"] - d["budget"]) / np.maximum(d["budget"], 1)
            d["success_tier"] = d["roi"].apply(assign_success_tier)

        # Signal transformations
        d["log_popularity"] = np.log1p(np.maximum(d["popularity"].fillna(0), 0))
        d["log_vote_count"] = np.log1p(np.maximum(d["vote_count"].fillna(0), 0))
        return d

    train_base = base_transforms(train_df)
    test_base = base_transforms(test_df)

    # Bayesian rating fitted on train
    mean_rating = float(train_base["vote_average"].mean())
    vote_threshold = float(train_base["vote_count"].quantile(IMDB_MIN_VOTES_QUANTILE))
    train_base["vote_confidence"] = compute_bayesian_rating(train_base, mean_rating, vote_threshold)
    test_base["vote_confidence"] = compute_bayesian_rating(test_base, mean_rating, vote_threshold)

    # Multi-hot genre encoding fitted on train
    genre_encoder = MultiHotGenreEncoder(min_frequency=10)
    genre_encoder.fit(train_base["genres_list"])
    train_genres = genre_encoder.transform(train_base["genres_list"])
    test_genres = genre_encoder.transform(test_base["genres_list"])

    # Director prior rolling aggregates (leakage-safe)
    dir_agg = LeakageSafeHistoricalAggregator(
        group_col="director", target_col="revenue", date_col="release_date_parsed"
    )
    dir_agg.fit(train_base)
    train_dir = dir_agg.transform_train(train_base)
    test_dir = dir_agg.transform(test_base)

    # Studio prior rolling aggregates (leakage-safe)
    studio_agg = LeakageSafeHistoricalAggregator(
        group_col="primary_production_company", target_col="revenue", date_col="release_date_parsed"
    )
    studio_agg.fit(train_base)
    train_studio = studio_agg.transform_train(train_base)
    test_studio = studio_agg.transform(test_base)

    # Combine all engineered features
    train_final = pd.concat([train_base, train_genres, train_dir, train_studio], axis=1)
    test_final = pd.concat([test_base, test_genres, test_dir, test_studio], axis=1)

    # Define feature manifest
    feature_manifest = {
        "pre_release_features": [
            "budget",
            "log_budget",
            "runtime",
            "cast_size",
            "production_company_count",
            "production_country_count",
            "is_international_coproduction",
            "is_franchise",
            "release_year",
            "release_month",
            "release_quarter",
            "release_day_of_week",
            "is_holiday_release",
            "director_prior_avg_revenue",
            "director_prior_film_count",
            "primary_production_company_prior_avg_revenue",
            "primary_production_company_prior_film_count",
        ]
        + list(train_genres.columns),
        "early_signal_features": [
            "popularity",
            "log_popularity",
            "vote_average",
            "vote_count",
            "log_vote_count",
            "vote_confidence",
        ],
        "targets": {
            "regression_target": "revenue",
            "regression_target_log": "log_revenue",
            "classification_target": "success_tier",
            "roi": "roi",
        },
        "genre_columns": list(train_genres.columns),
        "split_info": {
            "test_split_year": TEST_SPLIT_YEAR,
            "train_size": len(train_final),
            "test_size": len(test_final),
        },
    }

    return train_final, test_final, feature_manifest


def save_processed_datasets(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    manifest: Dict[str, Any],
) -> None:
    """Save processed parquet splits and manifest JSON to data/processed/."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Drop non-serializable complex objects from Parquet
    def prepare_for_parquet(df: pd.DataFrame) -> pd.DataFrame:
        d = df.copy()
        for col in ["genres_list", "cast_list", "production_companies_list", "production_countries_list"]:
            if col in d.columns:
                d[col] = d[col].apply(lambda x: "; ".join(x) if isinstance(x, list) else str(x))
        return d

    clean_train = prepare_for_parquet(train_df)
    clean_test = prepare_for_parquet(test_df)

    clean_train.to_parquet(TRAIN_DATA_PATH, engine="pyarrow", index=False)
    clean_test.to_parquet(TEST_DATA_PATH, engine="pyarrow", index=False)

    with open(FEATURE_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    logger.info("Saved train.parquet (%d rows) to %s", len(clean_train), TRAIN_DATA_PATH)
    logger.info("Saved test.parquet (%d rows) to %s", len(clean_test), TEST_DATA_PATH)
    logger.info("Saved feature manifest to %s", FEATURE_MANIFEST_PATH)
