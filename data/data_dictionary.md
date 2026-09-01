# CineForecast — Data Dictionary

This document defines the schema, field descriptions, data types, cleaning decisions, and known limitations for the raw dataset `dataset_1_collected_data.csv`.

---

## 1. Raw Dataset Overview
- **File**: `data/raw/dataset_1_collected_data.csv`
- **Total Records**: 9,999
- **Columns**: 15
- **Source**: TMDB API export (movies sorted by popularity desc)

---

## 2. Field Schema & Definitions

| Field | Raw Dtype | Description | Data Quality Notes & Handling Strategy |
|---|---|---|---|
| `id` | `int64` | TMDB Unique Identifier | 232 duplicate IDs present. Deduplicated by choosing the row with highest completeness score (fewest nulls and zero values). |
| `title` | `string` | Movie Title | Checked for sequel and franchise markers (e.g. "Part 2", "II", ":") to engineer `is_franchise`. |
| `budget` | `int64` | Production Budget in USD | 4,774 rows have `budget = 0`. These represent unrecorded financial data, not zero-dollar films. Excluded from supervised training. |
| `revenue` | `int64` | Box Office Revenue in USD | 4,432 rows have `revenue = 0`. Primary regression target. Excluded from training if missing. |
| `genres` | `string` | Stringified Python list of genre names | Serialized with single quotes (e.g. `"['Action', 'Drama']"`). Parsed safely with `ast.literal_eval`. Multi-hot encoded. |
| `runtime` | `int64` | Film duration in minutes | Zero and extreme sub-feature values (<40 min) filtered out from training. |
| `release_date` | `string` | Release date (`YYYY-MM-DD`) | 22 nulls. Contains future releases (up to 2031) and historical entries (<1990). Filtered to range `[1990, 2026]`. |
| `production_companies` | `string` | Stringified Python list of studio names | Parsed with `ast.literal_eval`. Primary company extracted; used for leakage-safe studio rolling revenue. |
| `production_countries` | `string` | Stringified Python list of country names | Parsed with `ast.literal_eval`. Used to derive `is_international_coproduction`. |
| `cast` | `string` | Stringified Python list of top-5 cast | Parsed with `ast.literal_eval`. Cast count and star presence derived. |
| `director` | `string` | Director Name | 69 nulls. Imputed as "Unknown". Used for leakage-safe rolling director revenue history. |
| `vote_average` | `float64` | TMDB Average User Rating (0-10) | Combined with `vote_count` using Bayesian IMDB formula to yield `vote_confidence`. Evaluated in leakage ablation. |
| `vote_count` | `int64` | Total TMDB User Votes | High skewness. Transformed via `log1p(vote_count)`. |
| `popularity` | `float64` | TMDB Proprietary Popularity Metric | Decaying metric updated continuously by TMDB. Log-transformed (`log1p(popularity)`) and treated as snapshot proxy. |
| `original_language` | `string` | ISO 639-1 Language Code | Tracks original production language (e.g. `en`, `es`, `fr`, `ja`). |

---

## 3. Derived & Engineered Target Fields

| Derived Field | Source | Type | Description |
|---|---|---|---|
| `roi` | `(revenue - budget) / budget` | `float64` | Financial return ratio. |
| `success_tier` | Derived from `roi` | `categorical` | Multi-class target: `Flop` (ROI < 0), `Break-even` (0 <= ROI < 1), `Hit` (1 <= ROI < 3), `Blockbuster` (ROI >= 3). |
| `log_revenue` | `log1p(revenue)` | `float64` | Primary continuous target for linear regression and gradient boosting. |
| `log_budget` | `log1p(budget)` | `float64` | Log-transformed production budget. |
| `director_prior_avg_revenue` | `director`, `release_date`, `revenue` | `float64` | Strict time-ordered historical mean revenue of past films by same director. |
| `primary_production_company_prior_avg_revenue` | `production_companies`, `release_date`, `revenue` | `float64` | Strict time-ordered historical mean revenue of past films by same studio. |
