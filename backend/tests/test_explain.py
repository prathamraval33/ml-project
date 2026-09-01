"""Tests for /api/shap explainability and ablation endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_get_global_shap(client: TestClient):
    """Test retrieving global SHAP feature importance summary."""
    response = client.get("/api/shap/global")
    assert response.status_code == 200
    data = response.json()

    assert "feature_importances" in data
    assert len(data["feature_importances"]) > 0
    assert "base_value_log" in data


def test_get_ablation_results(client: TestClient):
    """Test retrieving ablation study results."""
    response = client.get("/api/shap/ablation")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 6
