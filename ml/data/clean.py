"""Data cleaning and auditing pipeline for CineForecast.

Implements all Section 3.3 cleaning specifications:
1. Deduplication based on completeness score (fewest nulls/zeros).
2. Safe parsing of stringified Python list columns via parse_list_column.
3. Date parsing, chronological filtering (MIN_RELEASE_YEAR to MAX_RELEASE_YEAR).
4. Usable financial records identification (budget > 0 and revenue > 0).
5. Comprehensive audit metrics recording.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from ml.config import (
    INTERIM_DATA_PATH,
    MIN_RELEASE_YEAR,
    MAX_RELEASE_YEAR,
    MIN_RUNTIME_MINUTES,
    MAX_RUNTIME_MINUTES,
    LIST_COLUMNS,
)
from ml.data.parse_list_columns import parse_list_column, extract_primary_item

logger = logging.getLogger(__name__)


def compute_completeness_score(row: pd.Series) -> int:
    """Compute a data completeness score for a movie row.

    Higher scores indicate fewer missing, zero, or empty values.
    """
    score = 0
    # Financial data presence (highest value)
    if pd.notna(row.get("budget")) and row.get("budget") > 0:
        score += 3
    if pd.notna(row.get("revenue")) and row.get("revenue") > 0:
        score += 3

    # Metadata completeness
    if pd.notna(row.get("release_date")) and str(row.get("release_date")).strip():
        score += 2
    if pd.notna(row.get("director")) and str(row.get("director")).strip():
        score += 2
    if pd.notna(row.get("runtime")) and row.get("runtime", 0) > 0:
        score += 1
    if pd.notna(row.get("vote_count")) and row.get("vote_count", 0) > 0:
        score += 1
    if pd.notna(row.get("popularity")) and row.get("popularity", 0) > 0:
        score += 1
    return score


def deduplicate_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Deduplicate records by keeping the row with highest completeness per TMDB id.

    Args:
        df: Raw DataFrame.

    Returns:
        Tuple of (deduplicated DataFrame, audit metrics dict).
    """
    initial_rows = len(df)
    unique_ids = df["id"].nunique()
    duplicate_count = initial_rows - unique_ids

    logger.info("Found %d duplicate ID records out of %d total rows", duplicate_count, initial_rows)

    # Compute completeness score
    scores = df.apply(compute_completeness_score, axis=1)
    df_with_score = df.assign(_completeness=scores)

    # Sort descending by completeness and keep first per id
    deduped = (
        df_with_score.sort_values(by=["id", "_completeness"], ascending=[True, False])
        .drop_duplicates(subset=["id"], keep="first")
        .drop(columns=["_completeness"])
        .reset_index(drop=True)
    )

    metrics = {
        "initial_rows": initial_rows,
        "unique_ids": unique_ids,
        "duplicate_rows_removed": duplicate_count,
        "rows_after_dedup": len(deduped),
    }
    return deduped, metrics


def parse_and_clean_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean deduplicated dataset, parse list columns, format dates, and audit quality issues.

    Args:
        df: Deduplicated DataFrame.

    Returns:
        Tuple of (cleaned interim DataFrame, comprehensive audit report dict).
    """
    audit: Dict[str, Any] = {}
    total_deduped = len(df)

    # Audit zero financials
    both_zero = ((df["budget"] == 0) & (df["revenue"] == 0)).sum()
    budget_zero = (df["budget"] == 0).sum()
    revenue_zero = (df["revenue"] == 0).sum()
    both_positive = ((df["budget"] > 0) & (df["revenue"] > 0)).sum()

    audit["financial_stats"] = {
        "both_budget_revenue_zero": int(both_zero),
        "both_budget_revenue_zero_pct": round(float(both_zero / total_deduped * 100), 2),
        "budget_zero": int(budget_zero),
        "revenue_zero": int(revenue_zero),
        "usable_financial_records": int(both_positive),
        "usable_financial_records_pct": round(float(both_positive / total_deduped * 100), 2),
    }

    # Parse list columns
    df_clean = df.copy()
    for col in LIST_COLUMNS:
        if col in df_clean.columns:
            logger.info("Parsing list column: %s", col)
            df_clean[f"{col}_list"] = df_clean[col].apply(parse_list_column)

    # Derived genre attributes
    df_clean["primary_genre"] = df_clean["genres_list"].apply(
        lambda items: extract_primary_item(items, default="Unknown")
    )
    df_clean["genre_count"] = df_clean["genres_list"].apply(len)
    df_clean["cast_size"] = df_clean["cast_list"].apply(len)
    df_clean["production_company_count"] = df_clean["production_companies_list"].apply(len)
    df_clean["production_country_count"] = df_clean["production_countries_list"].apply(len)
    df_clean["primary_production_company"] = df_clean["production_companies_list"].apply(
        lambda items: extract_primary_item(items, default="Independent/Unknown")
    )

    # Parse and validate dates
    df_clean["release_date_parsed"] = pd.to_datetime(df_clean["release_date"], errors="coerce")
    null_dates = df_clean["release_date_parsed"].isna().sum()
    audit["null_release_dates"] = int(null_dates)

    df_clean["release_year"] = df_clean["release_date_parsed"].dt.year
    df_clean["release_month"] = df_clean["release_date_parsed"].dt.month
    df_clean["release_quarter"] = df_clean["release_date_parsed"].dt.quarter
    df_clean["release_day_of_week"] = df_clean["release_date_parsed"].dt.dayofweek

    # Future dates (> MAX_RELEASE_YEAR) and historical noise (< MIN_RELEASE_YEAR)
    future_movies = (df_clean["release_year"] > MAX_RELEASE_YEAR).sum()
    historical_movies = (df_clean["release_year"] < MIN_RELEASE_YEAR).sum()
    audit["future_dated_movies"] = int(future_movies)
    audit["historical_dated_movies"] = int(historical_movies)

    # Flag training eligibility
    df_clean["is_usable_for_training"] = (
        (df_clean["budget"] > 0)
        & (df_clean["revenue"] > 0)
        & (df_clean["release_year"] >= MIN_RELEASE_YEAR)
        & (df_clean["release_year"] <= MAX_RELEASE_YEAR)
        & (df_clean["runtime"] >= MIN_RUNTIME_MINUTES)
    )

    audit["training_eligible_records"] = int(df_clean["is_usable_for_training"].sum())
    audit["training_eligible_pct"] = round(
        float(df_clean["is_usable_for_training"].sum() / total_deduped * 100), 2
    )

    return df_clean, audit


def save_interim_dataset(df: pd.DataFrame, output_path: Path = INTERIM_DATA_PATH) -> Path:
    """Save cleaned and parsed interim dataset to Parquet format.

    Note: Complex list columns are stored with string representation alongside
    parsed attributes to ensure full Parquet compatibility across pyarrow versions.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Saving interim dataset to %s", output_path)

    # Prepare DataFrame for Parquet: convert list columns to json/string for clean serialization
    df_to_save = df.copy()
    for col in LIST_COLUMNS:
        list_col = f"{col}_list"
        if list_col in df_to_save.columns:
            df_to_save[list_col] = df_to_save[list_col].apply(lambda x: "; ".join(x) if isinstance(x, list) else "")

    df_to_save.to_parquet(output_path, engine="pyarrow", index=False)
    logger.info("Saved interim Parquet: %d rows to %s", len(df_to_save), output_path)
    return output_path
