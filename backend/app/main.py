"""FastAPI application entrypoint for CineForecast."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.db.base import Base, engine
from backend.app.routers import explain, movies, predict, trends, whatif
from backend.app.services.inference_service import inference_service

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("cineforecast.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hook: prepare database and pre-warm ML models."""
    logger.info("🎬 Initializing CineForecast API backend...")
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized at %s", settings.DATABASE_URL)
    # Pre-warm inference service
    _ = inference_service.reg_features
    logger.info("Champion ML models pre-warmed and ready for inference.")
    yield
    logger.info("🛑 Shutting down CineForecast API.")


app = FastAPI(
    title="CineForecast API",
    description=(
        "Production REST API for Film Revenue Forecasting, ROI Success Tier "
        "Classification, SHAP Model Explainability, and What-If Simulations."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(predict.router)
app.include_router(whatif.router)
app.include_router(explain.router)
app.include_router(movies.router)
app.include_router(trends.router)


@app.get("/", tags=["Health"])
def root():
    """Root status endpoint."""
    return {
        "service": "CineForecast API",
        "status": "online",
        "version": "1.0.0",
        "documentation": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """System health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "model_loaded": inference_service.regressor is not None,
    }
