"""FastAPI dependency injection utilities."""

from typing import Generator
from sqlalchemy.orm import Session

from backend.app.db.base import get_db
from backend.app.services.inference_service import InferenceService, inference_service


def get_inference_service() -> InferenceService:
    """Dependency provider for the singleton InferenceService."""
    return inference_service


__all__ = ["get_db", "get_inference_service", "Session"]
