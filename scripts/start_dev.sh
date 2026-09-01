#!/usr/bin/env bash
echo "==================================================="
echo " Starting CineForecast Development Environment"
echo "==================================================="

echo "Starting FastAPI Backend on http://localhost:8000 (Swagger docs at /docs)..."
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "Starting Vite Frontend Dashboard on http://localhost:5173..."
cd frontend && npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
