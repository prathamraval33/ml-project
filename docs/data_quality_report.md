# CineForecast — Data Quality & Cleaning Audit Report

**Generated Date**: 2026-09-01 12:04:04  
**Source File**: `data/raw/dataset_1_collected_data.csv`  
**Target Interim File**: `data/interim/deduplicated_parsed.parquet`

---

## 1. Executive Summary

A comprehensive, programmatic data quality audit was conducted on `dataset_1_collected_data.csv` in strict compliance with **masterprompt.md Section 3.3**. Every known data issue was reproduced, quantified, and resolved with documented, non-silent handling strategies.

| Metric | Raw Dataset | Deduplicated & Parsed | Final Usable for Training |
|---|---|---|---|
| **Total Rows** | 9,999 | 9,767 | 3,931 |
| **Unique Movies (`id`)** | 9,767 | 9,767 | 3,931 |
| **Both Budget & Revenue > 0** | 4,696 (46.96%) | 4,604 (47.14%) | 3,931 (100%) |
| **Both Budget & Revenue == 0** | 3,903 (39.03%) | 3,792 (38.82%) | 0 (0.00%) |

---

## 2. Detailed Audit of Section 3.3 Issues

### Issue 1 & 2: Missing Financial Values (Zeros)
- **Raw Observations**:
  - `budget == 0`: **4,774 rows (47.74%)**
  - `revenue == 0`: **4,432 rows (44.32%)**
  - `budget == 0` AND `revenue == 0`: **3,903 rows (39.03%)**
  - Usable rows (`budget > 0` AND `revenue > 0`): **4,696 rows (46.96%)**
- **Decision & Handling**:
  - In TMDB, a value of `0` in `budget` or `revenue` represents unrecorded/missing financial data, not actual zero-dollar production.
  - Rows lacking realized revenue cannot serve as ground truth for supervised regression. They are retained in `data/interim/deduplicated_parsed.parquet` flagged with `is_usable_for_training = False` so the dashboard can display catalog completeness analytics, but are excluded from the model training splits.

### Issue 3: Duplicate IDs
- **Raw Observations**:
  - Exactly **232 duplicate ID instances** across 464 rows.
  - Exactly 232 rows were 100% identical duplicates; the remaining duplicate IDs represented differing snapshot states.
- **Decision & Handling**:
  - Resolved via `compute_completeness_score()`: scored each duplicate row based on presence of non-zero budget, non-zero revenue, release date, director, and popularity.
  - Exactly one row per unique `id` was retained (the most complete record), reducing the dataset to **9,767 distinct films**.

### Issue 4: Release Date Anomalies & Future Releases
- **Raw Observations**:
  - Null release dates: **22 rows**.
  - Minimum release date: **1896-11-26** (historical cinema).
  - Maximum release date: **2031-12-17** (future scheduled releases up to 2031).
  - Future dated movies (`release_year > 2026`): **4 rows**.
  - Historical films (`release_year < 1990`): **1571 rows**.
- **Decision & Handling**:
  - Future-dated films (up to 2031) have no realized box office revenue and must not enter model training.
  - Historical releases prior to 1990 reflect a drastically different macroeconomic, theatrical, and inflationary era. A configurable threshold `MIN_RELEASE_YEAR = 1990` is enforced for training eligibility.

### Issue 5: Stringified Python List Columns
- **Raw Observations**:
  - `genres`, `production_companies`, `production_countries`, and `cast` were stored as stringified Python lists using single quotes (e.g. `"['Action', 'Drama']"`), rendering standard `json.loads` invalid.
- **Decision & Handling**:
  - Parsed using `ml/data/parse_list_columns.py` with `ast.literal_eval` wrapped in error handling, falling back to empty lists `[]`.
  - Extracted structured fields: `primary_genre`, `genre_count`, `cast_size`, `production_company_count`, `production_country_count`.

### Issue 6: TMDB Popularity & Vote Signals
- **Raw Observations**:
  - `popularity` is an unbounded, time-decaying metric recomputed daily by TMDB.
  - `vote_count` ranges from low single digits to tens of thousands.
- **Decision & Handling**:
  - Documented explicitly as a snapshot proxy.
  - Evaluated in Phase 4 via a formal **Leakage Ablation Study** (comparing pre-release-only models against models including early audience signals).

### Issue 7: Director & Runtime Nulls
- **Raw Observations**:
  - Missing director names: **69 rows**.
  - Zero runtime: **178 rows**.
- **Decision & Handling**:
  - Missing director imputed as `"Unknown"`.
  - Zero/sub-feature runtime (<40 minutes) excluded from training eligibility.

### Issue 8: Marketing Spend & Sentiment Absence
- **Observation**:
  - No marketing spend or sentiment columns exist in `dataset_1_collected_data.csv`.
- **Decision**:
  - **Path A Adopted**: We proceed strictly using the 15 real columns and robust engineered features. No synthetic columns are hallucinated.

---

## 3. Interim Dataset Output
- **File**: `data/interim/deduplicated_parsed.parquet`
- **Total Records**: 9,767
- **Columns**: 31
- **Training Eligible**: 3,931 (40.25%)
