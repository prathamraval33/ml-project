"""Pytest fixtures for CineForecast backend tests."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.base import Base, engine, SessionLocal
from backend.app.db.seed_from_processed import seed_database


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure tables and seed data exist for tests."""
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


@pytest.fixture(scope="module")
def client():
    """Test client for FastAPI app."""
    with TestClient(app) as c:
        yield c
