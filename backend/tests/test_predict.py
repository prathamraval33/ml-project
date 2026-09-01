"""Tests for /api/predict endpoint."""

import pytest
from fastapi.testclient import TestClient


def test_predict_success(client: TestClient):
    """Test standard valid prediction request."""
    payload = {
        "title": "Interstellar Odyssey",
        "budget": 120_000_000.0,
        "runtime": 145,
        "genres": ["Science Fiction", "Adventure", "Drama"],
        "release_date": "2026-11-20",
        "director": "Christopher Nolan",
        "cast_size": 8,
        "is_franchise": 0,
        "director_prior_avg_revenue": 450_000_000.0,
    }

    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Interstellar Odyssey"
    assert data["budget"] == 120_000_000.0
    assert data["predicted_revenue"] > 0
    assert data["predicted_tier"] in ["Flop", "Break-even", "Hit", "Blockbuster"]
    assert "top_positive_factors" in data
    assert len(data["top_positive_factors"]) > 0


def test_predict_invalid_budget(client: TestClient):
    """Test validation failure on non-positive budget."""
    payload = {
        "title": "Invalid Film",
        "budget": -500.0,
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422  # Unprocessable Entity
