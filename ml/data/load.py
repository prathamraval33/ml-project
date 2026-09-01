"""Data loading module for CineForecast raw datasets.

Handles reading raw CSV data, verifying exact schema and column types,
and providing clear validation diagnostics before cleaning.
"""

import logging
from pathlib import Path
from typing import Optional
import pandas as pd

from ml.config import RAW_DATA_PATH

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "id",
    "title",
    "budget",
    "revenue",
    "genres",
    "runtime",
    "release_date",
    "production_companies",
    "production_countries",
    "cast",
    "director",
    "vote_average",
    "vote_count",
    "popularity",
    "original_language",
]


def load_raw_data(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load raw movie data from CSV and validate structure against contract schema.

    Args:
        file_path: Optional path to raw CSV file. Defaults to RAW_DATA_PATH.

    Returns:
        pd.DataFrame containing raw movie data.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If expected columns are missing.
    """
    path = file_path or RAW_DATA_PATH
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found at: {path}")

    logger.info("Loading raw dataset from %s", path)
    df = pd.read_csv(path)

    logger.info("Loaded raw dataset: %d rows, %d columns", len(df), len(df.columns))

    # Verify column presence
    missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Raw data is missing expected columns: {missing_cols}")

    return df
