"""Tests for /api/whatif simulation endpoint."""

import pytest
from fastapi.testclient import TestClient


def test_whatif_standalone_simulation(client: TestClient):
    """Test What-If simulation with custom base params."""
    payload = {
        "base_params": {
            "title": "Indie Mystery",
            "budget": 10_000_000.0,
            "runtime": 100,
            "genres": ["Mystery", "Thriller"],
            "release_date": "2026-03-10",
        },
        "adjustments": {
            "budget": 25_000_000.0,
            "genres": ["Mystery", "Thriller", "Action"],
        },
    }

    response = client.post("/api/whatif", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["base_budget"] == 10_000_000.0
    assert data["modified_budget"] == 25_000_000.0
    assert "revenue_delta" in data
    assert "roi_delta" in data
    assert isinstance(data["tier_changed"], bool)
