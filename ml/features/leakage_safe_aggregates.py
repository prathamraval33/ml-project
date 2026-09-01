"""Leakage-safe rolling historical aggregates for CineForecast.

CRITICAL REQUIREMENT (masterprompt.md Section 3.4 & Section 6):
Aggregates like director_prior_avg_revenue and studio_prior_avg_revenue
must be computed with a strict time-ordered cutoff. A movie released at date T
must NEVER incorporate revenue from films released at or after date T.
"""

from typing import Optional, Dict
import pandas as pd
import numpy as np


class LeakageSafeHistoricalAggregator:
    """Computes time-ordered rolling historical averages for entities (director, studio).

    Ensures that for any movie at release_date T:
    prior_avg_revenue = mean(revenue of past films by same entity where release_date < T)
    If entity has no prior films before T, falls back to the global prior mean.
    """

    def __init__(
        self,
        group_col: str,
        target_col: str = "revenue",
        date_col: str = "release_date_parsed",
        min_prior_films: int = 1,
    ):
        self.group_col = group_col
        self.target_col = target_col
        self.date_col = date_col
        self.min_prior_films = min_prior_films
        self.history_df_: Optional[pd.DataFrame] = None
        self.global_historical_mean_: float = 0.0

    def fit(self, df: pd.DataFrame) -> "LeakageSafeHistoricalAggregator":
        """Store historical records from the training split.

        Args:
            df: Training DataFrame containing group_col, target_col, and date_col.

        Returns:
            self
        """
        valid = df.dropna(subset=[self.group_col, self.target_col, self.date_col]).copy()
        # Exclude placeholder groups
        valid = valid[~valid[self.group_col].isin(["", "Unknown", "Independent/Unknown"])]
        self.history_df_ = valid[[self.group_col, self.target_col, self.date_col]].copy()
        self.global_historical_mean_ = float(valid[self.target_col].mean()) if len(valid) > 0 else 0.0
        return self

    def transform_train(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute rolling prior aggregates for training data strictly using preceding rows in time.

        Args:
            df: Training DataFrame.

        Returns:
            pd.DataFrame with two new columns:
            - <group_col>_prior_avg_revenue
            - <group_col>_prior_film_count
        """
        out = pd.DataFrame(index=df.index)
        prior_avgs = []
        prior_counts = []

        # Sort indices chronologically
        sorted_indices = df.sort_values(by=self.date_col, ascending=True).index
        entity_records: Dict[str, list] = {}
        global_records: list = []

        idx_to_result = {}
        for idx in sorted_indices:
            row = df.loc[idx]
            entity = row.get(self.group_col)
            curr_rev = row.get(self.target_col)
            is_valid_entity = pd.notna(entity) and str(entity).strip() not in ["", "Unknown", "Independent/Unknown"]

            # Query prior history for this entity BEFORE updating with current film
            if is_valid_entity and entity in entity_records and len(entity_records[entity]) >= self.min_prior_films:
                avg_rev = float(np.mean(entity_records[entity]))
                count = len(entity_records[entity])
            else:
                # Fallback to cumulative global mean before this film
                avg_rev = float(np.mean(global_records)) if len(global_records) > 0 else self.global_historical_mean_
                count = 0

            idx_to_result[idx] = (avg_rev, count)

            # Update history with current film AFTER computing feature
            if pd.notna(curr_rev) and curr_rev > 0:
                global_records.append(curr_rev)
                if is_valid_entity:
                    if entity not in entity_records:
                        entity_records[entity] = []
                    entity_records[entity].append(curr_rev)

        # Restore original order
        for idx in df.index:
            avg_rev, count = idx_to_result.get(idx, (self.global_historical_mean_, 0))
            prior_avgs.append(avg_rev)
            prior_counts.append(count)

        col_prefix = self.group_col.replace("_list", "")
        out[f"{col_prefix}_prior_avg_revenue"] = prior_avgs
        out[f"{col_prefix}_prior_film_count"] = prior_counts
        return out

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute prior aggregates for test/validation rows using training history.

        Args:
            df: Evaluation/Test DataFrame.

        Returns:
            pd.DataFrame with prior aggregate columns.
        """
        if self.history_df_ is None:
            raise ValueError("Aggregator must be fitted on training data before transform.")

        out = pd.DataFrame(index=df.index)
        prior_avgs = []
        prior_counts = []

        # Pre-group training history
        history_grouped = self.history_df_.groupby(self.group_col)
        entity_means = history_grouped[self.target_col].mean().to_dict()
        entity_counts = history_grouped[self.target_col].count().to_dict()

        for _, row in df.iterrows():
            entity = row.get(self.group_col)
            if pd.notna(entity) and entity in entity_means:
                prior_avgs.append(float(entity_means[entity]))
                prior_counts.append(int(entity_counts[entity]))
            else:
                prior_avgs.append(self.global_historical_mean_)
                prior_counts.append(0)

        col_prefix = self.group_col.replace("_list", "")
        out[f"{col_prefix}_prior_avg_revenue"] = prior_avgs
        out[f"{col_prefix}_prior_film_count"] = prior_counts
        return out
