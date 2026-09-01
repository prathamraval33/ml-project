"""Tests for /api/movies browsing and detail endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_list_movies(client: TestClient):
    """Test listing movies with pagination."""
    response = client.get("/api/movies?page=1&size=10")
    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 1
    assert data["size"] == 10
    assert data["total"] > 0
    assert len(data["items"]) == 10
    assert "predicted_revenue" in data["items"][0]


def test_filter_movies_by_genre(client: TestClient):
    """Test filtering movies by genre."""
    response = client.get("/api/movies?genre=Action&size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0


def test_get_movie_not_found(client: TestClient):
    """Test requesting non-existent movie ID."""
    response = client.get("/api/movies/99999999")
    assert response.status_code == 404
