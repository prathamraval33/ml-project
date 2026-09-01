@echo off
echo ===================================================
echo  CineForecast: Running Full End-to-End Pipeline
echo ===================================================

echo [1/4] Running ML Pipeline (Clean, Features, Models, Tuning, SHAP)...
.venv\Scripts\python -m ml.pipeline
if %ERRORLEVEL% neq 0 (
    echo [ERROR] ML Pipeline failed.
    exit /b %ERRORLEVEL%
)

echo [2/4] Seeding Database with predictions...
.venv\Scripts\python -m backend.app.db.seed_from_processed
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Database seeding failed.
    exit /b %ERRORLEVEL%
)

echo [3/4] Running Pytest Suite...
.venv\Scripts\pytest ml/tests backend/tests -v
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Tests failed.
    exit /b %ERRORLEVEL%
)

echo [4/4] Building Frontend Dashboard...
cd frontend && npm run build && cd ..

echo ===================================================
echo  CineForecast Pipeline Complete Successfully!
echo ===================================================
