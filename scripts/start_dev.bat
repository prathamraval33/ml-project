@echo off
echo ===================================================
echo  Starting CineForecast Development Environment
echo ===================================================

echo Starting FastAPI Backend on http://localhost:8000 (Swagger docs at /docs)...
start "CineForecast Backend" cmd /k ".venv\Scripts\uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting Vite Frontend Dashboard on http://localhost:5173...
start "CineForecast Frontend" cmd /k "cd frontend && npm run dev"

echo Both services launched in separate windows.
