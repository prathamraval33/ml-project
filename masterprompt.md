# MASTERPROMPT.md
## CineForecast — Predictive Analytics for Film Revenue Forecasting
### Master Project Specification & AI Agent Execution Contract

**Version:** 1.0
**Owner:** [Your Name]
**Document type:** Single source of truth. Any AI coding agent (Claude Code, Cursor, Copilot Workspace, Devin, etc.) working on this repository MUST read this file in full before writing any code, and MUST re-read it before starting each new phase.
**Companion file:** `execution_tracker.md` (defined fully in Section 12) — the agent updates this file after every completed task. This masterprompt.md file is the specification; `execution_tracker.md` is the living progress log. They are separate files and must never be merged.

---

## 0. HOW THE AGENT MUST USE THIS DOCUMENT

1. Read this entire file before writing a single line of code.
2. Work strictly phase by phase, in the order defined in Section 8. Do not skip ahead to a later phase even if it seems easy, and do not start Phase N+1 until every task in Phase N is marked `DONE` in `execution_tracker.md`.
3. Before starting any phase, re-read that phase's section here in full.
4. After completing each individual task, immediately update `execution_tracker.md` (status, timestamp, files touched, notes) — do not batch updates at the end of a phase.
5. Never invent scope. If a requirement is ambiguous, make the most reasonable assumption, document it explicitly in `execution_tracker.md` under "Assumptions Log," and proceed — do not stall waiting for clarification unless it blocks all forward progress.
6. Never fabricate data, metrics, or results. If a script fails or a model underperforms, report the real numbers in the tracker — do not report invented "success" numbers.
7. All code must be production-grade: typed where the language supports it, documented, tested, and logged. This is explicitly NOT a throwaway notebook-only project — see Section 4 (Tech Stack) and Section 7 (Coding Standards).
8. Treat this as an **industry-level portfolio project** meant to be shown to recruiters/interviewers. Every folder, file name, and commit should look like it came from a real company's codebase, not a student script dump.

---

## 1. PROJECT IDENTITY

- **Project name:** CineForecast
- **Tagline:** Predictive Analytics for Film Revenue Forecasting
- **One-line pitch:** CineForecast is a full-stack, industry-grade machine learning platform that predicts a film's box office revenue and success tier from pre-release and early-release attributes (budget, cast, genre, timing, popularity signals), explains every prediction with SHAP, and surfaces the results through a big-data analytics dashboard with an interactive "what-if" simulator.
- **Category:** Applied Machine Learning + Full-Stack Data Product (advanced-level academic/portfolio project)
- **Primary academic/portfolio goals this project must demonstrate:**
  - End-to-end ML lifecycle: raw data → cleaning → feature engineering → model training → tuning → explainability → serving → visualization
  - Handling **real-world messy data** (not a clean textbook dataset — see Section 3.3, this dataset has zero-value fields, duplicates, missing values, malformed dates)
  - Regression AND classification modeling on the same feature set
  - Model interpretability (SHAP) as a first-class product feature, not an afterthought
  - A working REST API serving a trained model
  - A big-data-style analytics dashboard (multiple linked visualizations, filters, drill-downs)
  - Software engineering discipline: modular code, tests, config management, version control, documentation

---

## 2. PROBLEM STATEMENT

Predict a movie's **box office revenue** (regression target: `revenue`) and derive a **success tier classification** (Flop / Break-even / Hit / Blockbuster, derived from ROI) using features available before or shortly after release: budget, genre, runtime, cast, director, production companies/countries, release timing, and early audience signals (`vote_average`, `vote_count`, `popularity`).

The system must also let a user run **"what-if" simulations** — e.g., "what would the predicted revenue be if the budget were 20% higher, or the genre were changed?" — and see the model's reasoning via SHAP explanations, not just a black-box number.

---

## 3. DATASET — SOURCE OF TRUTH

### 3.1 File
- **Filename:** `dataset_1_collected_data.csv`
- **Location in repo:** `data/raw/dataset_1_collected_data.csv` (never modify this file in place — all cleaning happens in scripts that output to `data/processed/`)
- **Row count:** 9,999 rows
- **Column count:** 15 columns
- **Apparent source:** TMDB (The Movie Database) export style — confirmed by column shape and `id` values matching TMDB numeric IDs

### 3.2 Exact Schema (verified from actual file — agent must not assume different columns)

| Column | Dtype (as loaded) | Description | Notes |
|---|---|---|---|
| `id` | int64 | TMDB movie ID | **232 duplicate IDs found** — must deduplicate |
| `title` | string | Movie title | — |
| `budget` | int64 | Production budget in USD | **4,774 rows have budget = 0** (missing, not actually zero-budget films) |
| `revenue` | int64 | Box office revenue in USD | **4,432 rows have revenue = 0** (missing, not actual zero revenue) |
| `genres` | string (stringified Python list) | e.g. `"['Action', 'Adventure']"` | Must be parsed with `ast.literal_eval`, not `json.loads` (single quotes) |
| `runtime` | int64 | Runtime in minutes | Some rows have `runtime = 0` (missing) |
| `release_date` | string (`YYYY-MM-DD`) | Release date | **22 nulls**; date range in raw file spans **1896-11-26 to 2031-12-17** — the 2031 dates are upcoming/unreleased films and MUST be excluded from training (no ground-truth revenue possible), the 1896-era dates are legitimate historical entries but likely noise for a modern box-office model — apply a configurable `MIN_RELEASE_YEAR` filter (default 1990) |
| `production_companies` | string (stringified Python list) | List of studio names | Can be empty list `[]` |
| `production_countries` | string (stringified Python list) | List of countries | Can be empty list `[]` |
| `cast` | string (stringified Python list) | Top-billed cast names (appears capped at 5) | — |
| `director` | string | Director name | **69 nulls** |
| `vote_average` | float64 | TMDB average user rating (0-10) | — |
| `vote_count` | int64 | Number of TMDB votes | Low vote_count = low-confidence rating, must be handled (e.g. Bayesian-adjusted rating or use as a separate confidence feature) |
| `popularity` | float64 | TMDB popularity score (proprietary, unbounded, decays over time) | Volatile metric — TMDB recomputes this daily in production, so treat as a **snapshot proxy** feature only, document this limitation explicitly |
| `original_language` | string | ISO 639-1 language code | — |

### 3.3 Known Data Quality Issues (agent must handle every one of these explicitly in the cleaning pipeline, not silently)

1. **3,903 rows have BOTH budget=0 AND revenue=0** — these are unusable for the primary regression task and must be excluded from model training, but MAY be retained in a separate "incomplete records" table for dashboard completeness stats (e.g., "% of catalog with known financials").
2. **Only 4,696 of 9,999 rows (~47%) have both budget>0 and revenue>0** — this is the real, usable training set. The agent must NOT silently drop to this number without logging it clearly — this is a critical, reportable data limitation.
3. **232 duplicate `id` values** — investigate whether these are true duplicate rows or different snapshots; deduplicate by keeping the row with the most complete data (fewest nulls/zeros) per `id`.
4. **Future-dated releases (up to 2031)** — exclude any row where `release_date > today's date at time of dataset snapshot` from training (no realized revenue possible); these can power a separate "upcoming releases — predicted revenue" dashboard feature as a bonus.
5. **`genres`, `production_companies`, `production_countries`, `cast` are stringified Python lists, not JSON** — parsing must use `ast.literal_eval` inside a `try/except`, falling back to an empty list on malformed rows.
6. **`popularity` is a TMDB-proprietary, time-decaying score** — must be documented in the model card as a snapshot-in-time feature, not a stable signal.
7. **Multi-label `genres`** — a film can have multiple genres; must be multi-hot encoded, not single-label one-hot encoded. Decide and document a strategy for the "primary genre" used in groupby dashboard charts (e.g., first genre in the list).
8. **No marketing spend, no social sentiment, no trailer/hype data in this raw file** — unlike the earlier synthetic dataset discussed in this project's ideation phase, THIS real dataset does not include marketing spend or sentiment columns. The agent must NOT hallucinate these columns. Two allowed paths, to be decided in Phase 2 and logged in the tracker:
   - **Path A (recommended for a real-data-only project):** proceed using only the 15 real columns above plus engineered features derived from them (see Section 3.4). Document the absence of marketing/sentiment data as a stated project limitation.
   - **Path B (optional stretch goal, Phase 9):** enrich this dataset with a live TMDB API pull for additional fields (e.g. actual marketing/trailer data is not available from TMDB either — so Path B should instead pull additional TMDB fields such as `keywords`, `spoken_languages`, `belongs_to_collection` for franchise detection) — only attempt this after the core pipeline (Phases 1–7) is fully complete.

### 3.4 Feature Engineering Plan (derived from the REAL columns only)

| New feature | Derivation |
|---|---|
| `genre_list` | parsed list from `genres` |
| `primary_genre` | first element of `genre_list` |
| `genre_count` | number of genres tagged |
| `is_franchise` | 1 if `belongs_to_collection`-style signal can be inferred (title sequel pattern e.g. "Part 2", "II", or if pulled via Path B) — otherwise derive a proxy from duplicate director+similar-title patterns; document whichever method is used |
| `cast_size` | length of parsed `cast` list |
| `production_company_count` | length of parsed `production_companies` list |
| `production_country_count` | length of parsed `production_countries` list |
| `is_international_coproduction` | 1 if `production_country_count > 1` |
| `release_year`, `release_month`, `release_quarter`, `release_day_of_week` | parsed from `release_date` |
| `is_holiday_release` | 1 if `release_month` in [6, 7, 11, 12] |
| `director_prior_avg_revenue` | leakage-safe rolling average of a director's PAST films' revenue only (computed with a strict `release_date` cutoff — this is the single most important leakage trap in this dataset and must be implemented with a time-ordered groupby, never a global mean) |
| `studio_prior_avg_revenue` | same leakage-safe logic, per primary production company |
| `vote_confidence` | Bayesian-adjusted rating using `vote_average` and `vote_count` (e.g. IMDB weighted rating formula) to down-weight ratings based on very few votes |
| `log_budget`, `log_revenue`, `log_popularity`, `log_vote_count` | log1p transforms for skewed numeric fields |
| `roi` | `(revenue - budget) / budget` — used to derive `success_tier` |
| `success_tier` | Flop (`roi < 0`) / Break-even (`0 <= roi < 1`) / Hit (`1 <= roi < 3`) / Blockbuster (`roi >= 3`) |

**CRITICAL LEAKAGE WARNING the agent must respect at all times:** `vote_average`, `vote_count`, and `popularity` are TMDB metrics that continue to update AFTER release and can reflect post-release audience reaction — using them naively to predict revenue risks target leakage (a movie's popularity is partly driven BY its box office success). The agent must:
- Clearly document this limitation in the model card
- Train and report metrics for **two model variants**: (a) a pre-release-only feature set (budget, genre, cast, timing, studio/director history) and (b) an "early-signal" feature set that adds `vote_average`/`popularity`/`vote_count` — and explicitly compare/discuss the performance gap between them as evidence of the leakage effect. This comparison is itself a strong, advanced talking point for the project.

---

## 4. FULL TECHNOLOGY STACK (industry-standard, production-oriented — no shortcuts)

### 4.1 Data Engineering & ML
- **Language:** Python 3.11
- **Data manipulation:** pandas 2.x, numpy
- **ML modeling:** scikit-learn (pipelines, preprocessing, baseline models), XGBoost (primary model — `XGBRegressor`, `XGBClassifier`), CatBoost (comparison model, native categorical handling)
- **Hyperparameter tuning:** Optuna
- **Model interpretability:** SHAP (`TreeExplainer`)
- **Experiment tracking:** MLflow (local tracking server) — log every training run's params, metrics, and model artifact
- **Data validation:** Pydantic (for API schemas) + Great Expectations or `pandera` (for pipeline-stage data contracts — e.g., asserting `budget >= 0` after cleaning)
- **Notebook environment:** Jupyter (EDA and experimentation only — no production logic lives in notebooks)
- **Serialization:** joblib for models, Parquet (via pyarrow) for processed datasets (not CSV — Parquet preserves dtypes and is the industry-standard columnar format for a "big data" framing)

### 4.2 Backend / API
- **Framework:** FastAPI 0.115.x
- **Server:** Uvicorn (dev), Gunicorn + Uvicorn workers (prod)
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Database:** PostgreSQL 16
- **Validation:** Pydantic v2
- **Auth (if multi-user dashboard needed):** JWT via `python-jose` + `passlib[bcrypt]` (optional — only if Phase 8 scope includes user accounts; base project can run without auth)
- **Caching:** Redis (cache SHAP explanations and prediction results — SHAP computation is expensive, never recompute on every dashboard load)
- **Background jobs:** Celery + Redis broker (for retraining jobs / batch SHAP precomputation)
- **Testing:** pytest, httpx (async test client), pytest-cov (coverage reporting)
- **Logging:** Python `logging` module configured with structured JSON logs; `loguru` acceptable alternative

### 4.3 Frontend / Dashboard
- **Framework:** React 19 (Vite build tool)
- **Styling:** Tailwind CSS
- **Charts:** Recharts (primary), D3.js (only if a custom visualization Recharts can't handle is required, e.g. SHAP waterfall)
- **State/data fetching:** TanStack React Query (server state) + Zustand (local UI state)
- **Forms:** react-hook-form + zod validation (for the What-If Simulator inputs)
- **HTTP client:** Axios
- **Icons:** Lucide React

### 4.4 DevOps / Project Infrastructure
- **Version control:** Git, GitHub — conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`)
- **Containerization:** Docker + docker-compose (separate services: `backend`, `frontend`, `postgres`, `redis`, `mlflow`)
- **CI:** GitHub Actions — lint + test on every push (backend pytest, frontend eslint/build)
- **Environment config:** `.env` files per environment (never commit secrets — `.env.example` committed, `.env` gitignored)
- **Code quality:** `black` + `ruff` (Python formatting/linting), `eslint` + `prettier` (JS/React)
- **Pre-commit hooks:** `pre-commit` framework running black/ruff/eslint before every commit
- **Documentation:** this `masterprompt.md`, `execution_tracker.md`, per-phase `docs/` folder (model card, API docs via FastAPI's auto-generated OpenAPI/Swagger UI, architecture diagram)

---

## 5. INDUSTRY / PRODUCTION-LEVEL FOLDER STRUCTURE

```
cineforecast/
│
├── masterprompt.md                     # THIS FILE — full project specification
├── execution_tracker.md                # Living progress tracker, updated by agent per task
├── README.md                           # Public-facing project overview (for GitHub/recruiters)
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
├── pyproject.toml                      # Python project config (black/ruff settings, deps)
├── .pre-commit-config.yaml
│
├── .github/
│   └── workflows/
│       ├── backend-ci.yml              # lint + pytest on push
│       └── frontend-ci.yml             # eslint + build on push
│
├── data/
│   ├── raw/
│   │   └── dataset_1_collected_data.csv    # NEVER modified in place
│   ├── interim/
│   │   └── deduplicated_parsed.parquet     # after dedup + list-column parsing, before feature eng.
│   ├── processed/
│   │   ├── train.parquet
│   │   ├── test.parquet
│   │   └── feature_manifest.json           # documents every engineered feature + its source columns
│   └── data_dictionary.md                  # human-readable version of Section 3.2/3.3 above
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_data_quality_audit.ipynb         # documents every issue in Section 3.3 with evidence
│   ├── 03_feature_engineering_experiments.ipynb
│   ├── 04_baseline_modeling.ipynb
│   ├── 05_xgboost_catboost_comparison.ipynb
│   ├── 06_hyperparameter_tuning.ipynb
│   ├── 07_shap_analysis.ipynb
│   └── 08_leakage_ablation_study.ipynb     # the pre-release-only vs early-signal comparison
│
├── ml/
│   ├── __init__.py
│   ├── config.py                           # paths, constants, MIN_RELEASE_YEAR, random seeds
│   ├── data/
│   │   ├── __init__.py
│   │   ├── load.py                         # raw CSV loader
│   │   ├── clean.py                        # dedup, zero/null handling, date filtering
│   │   └── parse_list_columns.py           # ast.literal_eval helpers for genres/cast/companies
│   ├── features/
│   │   ├── __init__.py
│   │   ├── build_features.py               # implements Section 3.4 feature table
│   │   ├── leakage_safe_aggregates.py      # director_prior_avg_revenue, studio_prior_avg_revenue
│   │   └── encoders.py                     # multi-hot genre encoder, target encoders
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train_baseline.py               # linear regression baseline
│   │   ├── train_xgboost.py                # primary regressor + classifier
│   │   ├── train_catboost.py               # comparison model
│   │   ├── tune_optuna.py                  # hyperparameter search
│   │   └── registry/                       # joblib artifacts, gitignored except .gitkeep
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── metrics.py                      # RMSE/MAE/R², classification report
│   │   └── shap_explain.py                 # TreeExplainer wrapper, waterfall + summary plot generation
│   └── pipeline.py                         # orchestrates load→clean→feature→train→evaluate end-to-end
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                         # FastAPI app entrypoint
│   │   ├── config.py                       # settings via pydantic-settings, reads .env
│   │   ├── dependencies.py                 # shared DI (DB session, model service)
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── predict.py                  # POST /api/predict
│   │   │   ├── whatif.py                   # POST /api/whatif
│   │   │   ├── explain.py                  # GET /api/shap/{movie_id}
│   │   │   ├── movies.py                   # GET /api/movies (paginated, filterable)
│   │   │   └── trends.py                   # GET /api/trends (genre/time aggregates for dashboard)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── inference_service.py        # loads model once, runs predict()/explain()
│   │   │   └── cache_service.py            # Redis get/set wrappers
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                     # SQLAlchemy declarative base + session factory
│   │   │   ├── models.py                   # ORM models: Movie, Prediction, WhatIfSession
│   │   │   └── seed_from_processed.py      # loads processed parquet into Postgres
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── predict.py                  # Pydantic request/response models
│   │       └── movie.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── tests/
│   │   ├── test_predict.py
│   │   ├── test_whatif.py
│   │   ├── test_movies.py
│   │   └── conftest.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Overview.jsx                # predicted vs actual, headline metrics
│   │   │   ├── FeatureImportance.jsx       # global SHAP bar chart
│   │   │   ├── MovieExplorer.jsx           # searchable/filterable table + per-movie SHAP waterfall
│   │   │   ├── WhatIfSimulator.jsx         # interactive sliders/dropdowns
│   │   │   └── Trends.jsx                  # genre/time/country big-data style aggregate charts
│   │   ├── components/
│   │   │   ├── charts/
│   │   │   │   ├── PredictedVsActualScatter.jsx
│   │   │   │   ├── ShapSummaryBar.jsx
│   │   │   │   ├── ShapWaterfall.jsx
│   │   │   │   └── TrendLineChart.jsx
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   └── Header.jsx
│   │   │   └── ui/                         # small reusable primitives (Card, Badge, Slider, etc.)
│   │   ├── api/
│   │   │   └── client.js                   # Axios instance + React Query hooks
│   │   ├── store/
│   │   │   └── useUiStore.js               # Zustand store
│   │   └── styles/
│   │       └── index.css
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── docs/
│   ├── model_card.md                       # assumptions, limitations, leakage discussion, metrics table
│   ├── architecture_diagram.png
│   ├── api_reference.md                    # summary on top of FastAPI's auto Swagger docs
│   └── data_quality_report.md              # full writeup of Section 3.3 findings with numbers/plots
│
└── scripts/
    ├── run_full_pipeline.sh                # one command: clean → features → train → evaluate
    ├── seed_database.sh
    └── start_dev.sh                        # docker-compose up wrapper
```

---

## 6. CODING STANDARDS (non-negotiable)

- Every Python function has a docstring (purpose, args, returns) and type hints.
- No magic numbers in code — constants live in `ml/config.py` or `backend/app/config.py`.
- No business logic inside FastAPI route handlers — routes call service-layer functions only.
- Every new feature added to the model must be added to `data/processed/feature_manifest.json` with a one-line description and its source column(s).
- Every model training run must be logged to MLflow with parameters, metrics, and the artifact path — no "silent" retraining.
- All list-column parsing (`genres`, `cast`, `production_companies`, `production_countries`) must go through the single shared utility in `ml/data/parse_list_columns.py` — never re-implemented ad hoc in a notebook or script.
- Any leakage-safe aggregate (director/studio prior averages) must be computed with an explicit, tested, time-ordered cutoff — write a unit test that asserts no future data leaks into a past film's feature value.
- Frontend components are function components with hooks only — no class components.
- Every dashboard chart must handle empty/loading/error states, not just the happy path.

---

## 7. NON-NEGOTIABLE PROJECT CONSTRAINTS

1. Do not fabricate columns that don't exist in `dataset_1_collected_data.csv` (e.g., no marketing spend, no social sentiment score in the real pipeline — see Section 3.3 point 8).
2. Do not silently drop the ~53% of rows with missing budget/revenue — always log the exact count and percentage retained at every pipeline stage.
3. Do not train on `vote_average`/`vote_count`/`popularity` without explicitly running and reporting the leakage ablation study (Section 3.4).
4. Do not skip the time-based train/test split in favor of a random split.
5. Do not commit `data/raw/`, trained model binaries, `.env`, or `node_modules` to git — all covered in `.gitignore`.
6. Do not merge `masterprompt.md` and `execution_tracker.md` into one file — they serve different purposes and must remain separate.

---

## 8. PHASE-WISE EXECUTION PLAN

### **Phase 0 — Environment & Repo Setup**
- Initialize git repo with the folder structure in Section 5 (empty placeholder files/`__init__.py` where needed)
- Set up `pyproject.toml`, `.pre-commit-config.yaml`, `.gitignore`, `.env.example`
- Set up `docker-compose.yml` with `postgres`, `redis`, `backend`, `frontend`, `mlflow` services (can start as stubs)
- Create `execution_tracker.md` from the template in Section 12
- **Exit criteria:** `docker-compose up` starts all containers without error (even if backend/frontend are placeholder "hello world" apps)

### **Phase 1 — Data Audit & Cleaning**
- Load `dataset_1_collected_data.csv`, reproduce every finding in Section 3.3 with code (not just trust this document — verify counts match)
- Write `ml/data/load.py`, `ml/data/clean.py`, `ml/data/parse_list_columns.py`
- Produce `data/interim/deduplicated_parsed.parquet`
- Write `docs/data_quality_report.md` documenting every issue found with exact counts/percentages and the handling decision made for each
- **Exit criteria:** deduplicated, parsed, date-filtered interim dataset saved; data quality report complete with real numbers

### **Phase 2 — EDA**
- `notebooks/01_eda.ipynb`: distributions, correlations, revenue by genre/studio/timing, missingness patterns
- Decide and document (in `execution_tracker.md` Assumptions Log) the Path A vs Path B decision from Section 3.3 point 8
- **Exit criteria:** EDA notebook complete with at least 10 documented insights that inform feature engineering

### **Phase 3 — Feature Engineering**
- Implement every feature in Section 3.4 in `ml/features/`
- Implement and unit-test the leakage-safe director/studio prior-average aggregates
- Produce `data/processed/train.parquet`, `data/processed/test.parquet` (time-based split), and `data/processed/feature_manifest.json`
- **Exit criteria:** processed train/test parquet files exist; feature manifest complete; leakage-safety unit test passes

### **Phase 4 — Baseline & Primary Modeling**
- `ml/models/train_baseline.py` — Linear Regression on log-revenue, log metrics to MLflow
- `ml/models/train_xgboost.py` — XGBRegressor (revenue) + XGBClassifier (success_tier)
- `ml/models/train_catboost.py` — comparison model
- Run and report the **leakage ablation study**: pre-release-only feature set vs early-signal feature set, both models, metrics compared side by side
- **Exit criteria:** all models trained, logged to MLflow, metrics table written into `docs/model_card.md`

### **Phase 5 — Hyperparameter Tuning & Interpretability**
- `ml/models/tune_optuna.py` — tune the best-performing model family from Phase 4
- `ml/evaluation/shap_explain.py` — global summary plot + per-movie waterfall generation, cached to disk
- **Exit criteria:** tuned model outperforms Phase 4 baseline on held-out test set; SHAP artifacts generated for every test-set movie

### **Phase 6 — Backend API**
- Implement all routers/services/db models per Section 5 structure
- Seed PostgreSQL from `data/processed/` via `seed_from_processed.py`
- Write pytest suite covering every endpoint (happy path + at least one error case each)
- **Exit criteria:** `pytest` passes with meaningful coverage (target >80% on `backend/app/`); Swagger UI at `/docs` fully functional

### **Phase 7 — Frontend Dashboard**
- Build all five pages per Section 5 structure, wired to the live backend
- Implement the What-If Simulator end-to-end (form → `/api/whatif` → live-updating result)
- **Exit criteria:** all pages render real data from the backend, no hardcoded/mock values remain anywhere in the frontend

### **Phase 8 — Polish, Testing, Documentation**
- Finalize `docs/model_card.md`, `docs/architecture_diagram.png`, `docs/api_reference.md`, root `README.md`
- Add GitHub Actions CI workflows
- Full run-through of `scripts/run_full_pipeline.sh` and `scripts/start_dev.sh` from a clean clone to confirm reproducibility
- **Exit criteria:** a stranger can clone the repo, follow the README, and get the full stack running with the real dataset

### **Phase 9 — Stretch Goals (optional, only after Phase 8 is fully DONE)**
- Path B enrichment: pull additional TMDB fields for franchise/collection detection
- Add Celery background retraining job
- Add basic auth for a multi-user dashboard
- Deploy to a cloud host (Render/Railway/Fly.io for backend, Vercel/Netlify for frontend)

---

## 9. SUCCESS METRICS / TARGETS

- Regression: report RMSE, MAE, R² on both log-revenue scale and back-transformed USD scale, on the held-out (2023+) test set
- Classification (`success_tier`): report accuracy, macro-F1, and full confusion matrix, given known class imbalance
- Explicit numeric comparison table: pre-release-only model vs early-signal model (the leakage ablation)
- No specific "must beat X% accuracy" target is imposed — the metric that matters most for grading/portfolio purposes is **rigor and honesty of reporting**, not an inflated number

---

## 10. MODEL CARD REQUIREMENTS (`docs/model_card.md` must include)

- Intended use and out-of-scope use
- Full data description (Section 3 of this document, condensed)
- The ~47% usable-row limitation, stated plainly
- The leakage ablation results and what they imply about which features are safe to use in a true pre-release prediction scenario
- Known limitations: no marketing spend/sentiment data available in this real dataset; `popularity` is a decaying, snapshot-in-time proprietary score; small usable-row count for an "advanced" model relative to production-scale systems
- Ethical note: predictions should not be read as guaranteeing a film's success/failure — many unmodeled factors (marketing execution, competitive release calendar changes after data collection, critical reception) affect real-world outcomes

---

## 11. TECH STACK DECISION RATIONALE (brief, for the agent to reuse in documentation/interviews)

- **XGBoost over pure neural net:** tabular data of this size (~4.7k usable rows) strongly favors gradient boosting; a neural net would overfit and add complexity without benefit.
- **CatBoost as comparison:** native categorical handling (genre, studio, director) avoids high-cardinality one-hot blowup, worth benchmarking against XGBoost's encoded approach.
- **FastAPI over Flask/Django:** async support, automatic OpenAPI docs, Pydantic validation — matches the rest of this candidate's existing stack (see related `placement-portal` project using the same backend stack) for consistency across their portfolio.
- **PostgreSQL over MongoDB:** the data is inherently relational (movies ↔ predictions ↔ what-if sessions), and SQL aggregate queries power the Trends dashboard page directly.
- **Parquet over CSV for processed data:** preserves dtypes, compresses well, standard for a "big data" framing even at this dataset's modest scale — demonstrates awareness of tooling that scales.

---

## 12. execution_tracker.md — REQUIRED FORMAT (the agent creates this as a SEPARATE file, not part of this one)

The agent must create `execution_tracker.md` at the project root using this exact structure, and update it continuously:

```markdown
# CineForecast — Execution Tracker

Last updated: [ISO timestamp, updated by agent on every change]
Overall progress: [X / Y tasks complete] ([%]%)

## Phase 0 — Environment & Repo Setup — STATUS: [NOT STARTED / IN PROGRESS / DONE]
- [ ] Task description — STATUS — timestamp — files touched — notes

## Phase 1 — Data Audit & Cleaning — STATUS: [...]
- [ ] ...

... (one section per phase from Section 8 above, same task granularity) ...

## Assumptions Log
- [timestamp] Assumption made and why

## Blockers / Open Questions
- [timestamp] Description of blocker, current workaround if any

## Data Quality Findings (running log, filled during Phase 1)
- [finding, exact count/percentage, decision made]

## Model Metrics Log (running log, filled during Phase 4-5)
- [model name, feature set, RMSE, MAE, R², date trained]
```

Every checkbox task must be updated to `[x]` with a timestamp and a one-line note the moment it is completed — never marked done in bulk at the end of a session.

---

## 13. FINAL INSTRUCTION TO THE AGENT

Begin at Phase 0. Confirm the folder structure in Section 5 is created before writing any logic. Create `execution_tracker.md` per Section 12 before starting Phase 1. Do not proceed to Phase 1 data work until Phase 0's exit criteria are met and logged. Work through every phase in order, updating the tracker after every single task, and do not report a phase as complete unless its stated exit criteria are genuinely, verifiably met.

**END OF MASTERPROMPT.md**
