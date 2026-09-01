"""Feature encoders for CineForecast.

Implements multi-hot encoding for multi-label genres and categorical transformations
fitted strictly on training splits to prevent data leakage.
"""

from typing import List, Optional
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class MultiHotGenreEncoder(BaseEstimator, TransformerMixin):
    """Multi-hot encoder for films with multiple genre tags.

    Learns the vocabulary of genres from the training set and transforms
    lists of genres into binary indicator columns (genre_<name>).
    """

    def __init__(self, min_frequency: int = 10):
        self.min_frequency = min_frequency
        self.genres_: List[str] = []

    def fit(self, X: pd.Series, y: Optional[pd.Series] = None) -> "MultiHotGenreEncoder":
        """Fit encoder by discovering frequent genres.

        Args:
            X: Series of genre lists (or semicolon-separated genre strings).
            y: Ignored.

        Returns:
            self
        """
        counts: dict = {}
        for item in X:
            if isinstance(item, list):
                genres = item
            elif isinstance(item, str):
                genres = [g.strip() for g in item.split(";") if g.strip()]
            else:
                genres = []

            for g in set(genres):
                counts[g] = counts.get(g, 0) + 1

        # Keep genres meeting minimum frequency threshold
        self.genres_ = sorted([g for g, count in counts.items() if count >= self.min_frequency])
        return self

    def transform(self, X: pd.Series) -> pd.DataFrame:
        """Transform genre lists into a multi-hot DataFrame.

        Args:
            X: Series of genre lists (or semicolon-separated strings).

        Returns:
            pd.DataFrame with binary columns prefixed by 'genre_'.
        """
        data = []
        for item in X:
            if isinstance(item, list):
                genres = set(item)
            elif isinstance(item, str):
                genres = set(g.strip() for g in item.split(";") if g.strip())
            else:
                genres = set()

            row = [1 if g in genres else 0 for g in self.genres_]
            data.append(row)

        cols = [f"genre_{g.lower().replace(' ', '_').replace('-', '_')}" for g in self.genres_]
        return pd.DataFrame(data, columns=cols, index=X.index)
