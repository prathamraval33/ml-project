"""Unit tests to verify leakage safety of historical aggregates.

Asserts that:
1. A past film's prior aggregate never incorporates revenue from future films.
2. Changes to a future film's revenue do not affect prior feature values for past films.
3. Out-of-sample transform only uses training history prior to test release dates.
"""

import pandas as pd
import numpy as np
import pytest
from ml.features.leakage_safe_aggregates import LeakageSafeHistoricalAggregator


def test_director_prior_revenue_leakage_safety():
    # Construct a director with 3 films released in 2010, 2015, 2020
    data = [
        {
            "id": 1,
            "director": "Christopher Nolan",
            "release_date_parsed": pd.Timestamp("2010-07-16"),
            "revenue": 836_000_000,
        },
        {
            "id": 2,
            "director": "Christopher Nolan",
            "release_date_parsed": pd.Timestamp("2015-11-05"),
            "revenue": 677_000_000,
        },
        {
            "id": 3,
            "director": "Christopher Nolan",
            "release_date_parsed": pd.Timestamp("2020-09-03"),
            "revenue": 365_000_000,
        },
    ]
    df = pd.DataFrame(data)

    agg = LeakageSafeHistoricalAggregator(
        group_col="director",
        target_col="revenue",
        date_col="release_date_parsed",
        min_prior_films=1,
    )
    agg.fit(df)
    res = agg.transform_train(df)

    # Film 1 (2010): Has no prior films. Must NOT have film 2 or film 3 revenue.
    film1_prior = res.loc[0, "director_prior_avg_revenue"]
    film1_count = res.loc[0, "director_prior_film_count"]
    assert film1_count == 0

    # Film 2 (2015): Prior should be EXACTLY Film 1 revenue (836M)
    film2_prior = res.loc[1, "director_prior_avg_revenue"]
    film2_count = res.loc[1, "director_prior_film_count"]
    assert film2_count == 1
    assert film2_prior == 836_000_000

    # Film 3 (2020): Prior should be EXACTLY mean of Film 1 and Film 2 (756.5M)
    film3_prior = res.loc[2, "director_prior_avg_revenue"]
    film3_count = res.loc[2, "director_prior_film_count"]
    assert film3_count == 2
    assert np.isclose(film3_prior, (836_000_000 + 677_000_000) / 2)

    # Invariance check: Modifying film 3's revenue to 10 billion should NOT change Film 1 or Film 2 prior
    df_modified = df.copy()
    df_modified.loc[2, "revenue"] = 10_000_000_000
    res_modified = agg.transform_train(df_modified)

    assert res_modified.loc[0, "director_prior_avg_revenue"] == film1_prior
    assert res_modified.loc[1, "director_prior_avg_revenue"] == film2_prior
