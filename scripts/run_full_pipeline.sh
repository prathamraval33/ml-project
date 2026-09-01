#!/usr/bin/env bash
set -e

echo "==================================================="
echo " CineForecast: Running Full End-to-End Pipeline"
echo "==================================================="

echo "[1/4] Running ML Pipeline (Clean, Features, Models, Tuning, SHAP)..."
python -m ml.pipeline

echo "[2/4] Seeding Database with predictions..."
python -m backend.app.db.seed_from_processed

echo "[3/4] Running Pytest Suite..."
pytest ml/tests backend/tests -v

echo "[4/4] Building Frontend Dashboard..."
cd frontend && npm run build && cd ..

echo "==================================================="
echo " CineForecast Pipeline Complete Successfully!"
echo "==================================================="
