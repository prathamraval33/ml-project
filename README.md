# 🎬 CineForecast: Predictive Analytics for Film Revenue Forecasting

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF.svg)](https://vitejs.dev)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-FF6600.svg)](https://xgboost.readthedocs.io)
[![SHAP](https://img.shields.io/badge/SHAP-TreeExplainer-FF0055.svg)](https://shap.readthedocs.io)
[![Pytest](https://img.shields.io/badge/pytest-Passing-brightgreen.svg)](https://docs.pytest.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**CineForecast** is a full-stack, industry-grade machine learning platform that predicts a film's box office revenue and financial return tier from pre-release attributes (budget, cast, multi-label genres, release timing, studio/director priors), explains predictions with SHAP (SHapley Additive exPlanations), and surfaces insights through an interactive big-data analytics dashboard with a real-time What-If scenario simulator.

---

## 🏛️ System Architecture

```
                                  +---------------------------------------+
                                  |     Raw TMDB Box Office Catalog       |
                                  |   (9,999 Raw Records / 15 Columns)    |
                                  +-------------------+-------------------+
                                                      |
                                          [1. Data Audit & Cleaning]
                                  • Completeness-based deduplication
                                  • Date range validation & zero filtering
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |   Interim Dataset (3,931 Clean Films) |
                                  +-------------------+-------------------+
                                                      |
                                          [2. Leakage-Safe Engineering]
                                  • Chronological rolling priors (Director/Studio)
                                  • Multi-hot genres & calendar seasonality
                                  • Temporal train/test split (Train: 1990-2022, Test: 2023-2025)
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |       Model Training & Tuning         |
                                  |  • Baseline Ridge Regressor           |
                                  |  • Champion XGBoost (Optuna Tuned)    |
                                  |  • CatBoost Comparison Benchmark      |
                                  |  • Target Leakage Ablation Study      |
                                  +-------------------+-------------------+
                                                      |
                                         [3. Interpretability & Serving]
                                  • TreeExplainer SHAP waterfall caching
                                  • SQLite / PostgreSQL relational DB
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |          FastAPI REST Engine          |
                                  |   /api/predict • /api/whatif • /api/shap
                                  |   /api/movies  • /api/trends          |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |        React / Vite Dashboard         |
                                  |  • Executive Overview & Scatter Plot  |
                                  |  • Global SHAP & Ablation Studio      |
                                  |  • Catalog Explorer & Waterfall Drawers|
                                  |  • Interactive What-If Simulator      |
                                  |  • Macro Industry Trends Analytics    |
                                  +---------------------------------------+
```

---

## 🚀 Key Engineering & ML Highlights

1. **Handling Messy Real-World Data**: Audited and documented real-world anomalies (47.7% missing budget, 44.3% missing revenue, 232 duplicates, malformed stringified Python lists, future release dates).
2. **Strict Leakage Prevention**: Rolling director and studio revenue priors are computed strictly with time-ordered chronological cutoffs, preventing future box office success from leaking into historical averages.
3. **Leakage Ablation Study**: Quantitatively proves the inflation effect of post-release audience reaction (`vote_count`, `popularity`) vs pure pre-release predictors.
4. **First-Class Explainability**: Every prediction is paired with SHAP waterfall contributions (positive value drivers vs negative drags).
5. **Interactive What-If Studio**: Live sensitivity analysis allowing producers and analysts to dynamically tune budgets, change genres, shift release dates, and immediately view ROI and tier impact.
6. **Dark Void Design System**: Monolithic high-density dark UI styled strictly with bespoke design tokens inspired by modern design principles.

---

## 📊 Benchmark Model Performance

Evaluated on held-out test films (2023–2025 releases, $N=383$):

| Model | Feature Set | Test $R^2$ (Log) | Test RMSE (Log) | Test MAE (Log) | Pearson $r$ |
|---|---|---|---|---|---|
| **Ridge Regression** | Pre-Release (Clean) | 0.4021 | 1.6950 | 1.1609 | 0.6536 |
| **CatBoost** | Pre-Release (Clean) | 0.3943 | 1.7061 | 1.2109 | 0.6410 |
| **XGBoost (Champion)** | **Pre-Release (Clean)** | **0.3747** | **1.7334** | **1.2236** | **0.6267** |
| **CatBoost (Ablation)** | Early-Signal (+Popularity) | 0.4047 | 1.6914 | 1.2174 | 0.6939 |

---

## ⚡ Quickstart & Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Clone & Set Up Python Environment
```bash
git clone https://github.com/your-username/cineforecast.git
cd cineforecast

# Create virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Full ML Pipeline & Seed Database
```bash
# Windows
scripts\run_full_pipeline.bat

# macOS / Linux
chmod +x scripts/run_full_pipeline.sh
./scripts/run_full_pipeline.sh
```

### 3. Launch the Backend & Frontend Dev Servers
```bash
# Windows
scripts\start_dev.bat

# macOS / Linux
chmod +x scripts/start_dev.sh
./scripts/start_dev.sh
```

- **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
- **FastAPI Backend & Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Running Automated Tests

```bash
# Run all ML leakage safety and backend API unit tests
pytest ml/tests backend/tests -v
```

---

## 📁 Repository Structure

```
cineforecast/
├── backend/                  # FastAPI REST API
│   ├── app/
│   │   ├── config.py         # Pydantic Settings
│   │   ├── dependencies.py   # Dependency injection
│   │   ├── db/               # SQLAlchemy models & SQLite/Postgres seeder
│   │   ├── routers/          # /predict, /whatif, /shap, /movies, /trends
│   │   ├── schemas/          # Pydantic v2 schemas
│   │   └── services/         # Inference & Cache services
│   └── tests/                # Pytest API test suite
├── data/
│   ├── raw/                  # Immutable raw dataset
│   ├── interim/              # Deduplicated & parsed parquet
│   └── processed/            # Train/test splits & feature_manifest.json
├── docs/
│   ├── model_card.md         # Full ML Model Card
│   ├── api_reference.md      # REST API Reference
│   └── data_quality_report.md# Phase 1 Data Audit
├── frontend/                 # Vite + React 18 + Tailwind CSS Dashboard
│   ├── src/
│   │   ├── api/              # Axios API client
│   │   ├── components/       # Layout, UI primitives, and Recharts
│   │   ├── pages/            # 5 Core Dashboard Views
│   │   ├── store/            # Zustand UI store
│   │   └── styles/           # Design tokens in index.css
├── ml/
│   ├── data/                 # Load, clean & list parser
│   ├── features/             # Leakage-safe feature engineering & encoders
│   ├── models/               # Baseline, XGBoost, CatBoost, Optuna tuning
│   ├── evaluation/           # Metrics, Ablation study, SHAP TreeExplainer
│   └── pipeline.py           # Full end-to-end ML orchestrator
└── scripts/                  # Cross-platform runner scripts
```

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.
