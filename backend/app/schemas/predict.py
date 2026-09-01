"""Pydantic schemas for prediction, what-if simulations, and SHAP explainability."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Input payload for movie revenue prediction."""

    title: Optional[str] = Field(default="Untitled Film", description="Movie title")
    budget: float = Field(..., gt=0, description="Production budget in USD")
    runtime: int = Field(default=110, ge=40, le=360, description="Runtime in minutes")
    genres: List[str] = Field(default_factory=lambda: ["Drama"], description="List of genre names")
    release_date: Optional[str] = Field(default="2026-07-15", description="Release date (YYYY-MM-DD)")
    director: Optional[str] = Field(default="Unknown", description="Director name")
    cast_size: Optional[int] = Field(default=5, ge=1, le=50, description="Number of credited cast members")
    production_company_count: Optional[int] = Field(default=2, ge=1, le=20, description="Number of production studios")
    production_country_count: Optional[int] = Field(default=1, ge=1, le=10, description="Number of production countries")
    is_franchise: Optional[int] = Field(default=0, ge=0, le=1, description="Franchise indicator (0 or 1)")
    director_prior_avg_revenue: Optional[float] = Field(default=0.0, ge=0, description="Historical director avg revenue")
    director_prior_film_count: Optional[int] = Field(default=0, ge=0, description="Number of prior films by director")
    primary_production_company_prior_avg_revenue: Optional[float] = Field(default=0.0, ge=0, description="Historical studio avg revenue")
    primary_production_company_prior_film_count: Optional[int] = Field(default=0, ge=0, description="Number of prior films by studio")


class ShapContribution(BaseModel):
    """Single feature contribution in a SHAP explanation."""

    feature: str
    value: float
    shap_value: float
    abs_shap: float


class PredictResponse(BaseModel):
    """Prediction outcome including revenue, ROI, success tier, and top SHAP drivers."""

    title: str
    budget: float
    predicted_revenue: float
    predicted_roi: float
    predicted_tier: str  # Flop, Break-even, Hit, Blockbuster
    confidence_tier_probabilities: Optional[Dict[str, float]] = None
    base_value: float
    top_positive_factors: List[ShapContribution]
    top_negative_factors: List[ShapContribution]
    all_contributions: Optional[List[ShapContribution]] = None


class WhatIfRequest(BaseModel):
    """Payload for sensitivity / What-If analysis comparing baseline with simulated changes."""

    base_movie_id: Optional[int] = Field(default=None, description="Optional existing movie ID as base")
    base_params: Optional[PredictRequest] = Field(default=None, description="Base film parameters")
    adjustments: Dict[str, Any] = Field(..., description="Key-value adjustments (e.g. {'budget': 150000000, 'genres': ['Action', 'Sci-Fi']})")


class WhatIfResponse(BaseModel):
    """Outcome of what-if simulation showing comparative metrics and deltas."""

    base_budget: float
    modified_budget: float
    base_predicted_revenue: float
    modified_predicted_revenue: float
    revenue_delta: float
    revenue_delta_percent: float
    base_predicted_roi: float
    modified_predicted_roi: float
    roi_delta: float
    base_predicted_tier: str
    modified_predicted_tier: str
    tier_changed: bool
    modified_top_positive_factors: List[ShapContribution]
    modified_top_negative_factors: List[ShapContribution]


class ShapExplanationResponse(BaseModel):
    """Full SHAP waterfall explanation response for a specific movie."""

    movie_id: int
    title: str
    base_value_log: float
    base_value_usd: float
    predicted_log_revenue: float
    predicted_revenue_usd: float
    contributions: List[ShapContribution]
    top_positive: List[ShapContribution]
    top_negative: List[ShapContribution]
