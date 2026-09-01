"""Tests for /api/trends big data analytics endpoint."""

import pytest
from fastapi.testclient import TestClient


def test_get_trends(client: TestClient):
    """Test retrieving aggregate trend analytics."""
    response = client.get("/api/trends")
    assert response.status_code == 200
    data = response.json()

    assert "genre_trends" in data
    assert len(data["genre_trends"]) > 0
    assert "yearly_trends" in data
    assert len(data["yearly_trends"]) > 0
    assert "seasonality_trends" in data
    assert len(data["seasonality_trends"]) > 0
    assert "headline_kpis" in data
    assert data["headline_kpis"]["total_catalog_size"] > 0
