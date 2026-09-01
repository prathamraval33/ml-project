"""Pydantic schemas for Movie browsing and Trends analytics."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MovieDetail(BaseModel):
    """Detailed movie view."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    budget: float
    revenue: float
    runtime: Optional[int]
    release_date: Optional[str]
    release_year: Optional[int]
    release_month: Optional[int]
    genres: Optional[str]
    primary_genre: Optional[str]
    director: Optional[str]
    production_companies: Optional[str]
    production_countries: Optional[str]
    original_language: Optional[str]
    popularity: Optional[float]
    vote_average: Optional[float]
    vote_count: Optional[int]
    is_franchise: int
    is_holiday_release: int
    roi: Optional[float]
    success_tier: Optional[str]
    predicted_revenue: Optional[float]
    predicted_roi: Optional[float]
    predicted_tier: Optional[str]
    split: Optional[str]


class MovieListResponse(BaseModel):
    """Paginated list of movies."""

    items: List[MovieDetail]
    total: int
    page: int
    size: int
    total_pages: int


class GenreTrend(BaseModel):
    """Aggregated financial trend for a specific genre."""

    genre: str
    movie_count: int
    avg_budget: float
    avg_revenue: float
    avg_roi: float
    hit_rate_percent: float


class YearlyTrend(BaseModel):
    """Aggregated financial trend across years."""

    release_year: int
    movie_count: int
    total_revenue: float
    avg_revenue: float
    avg_budget: float
    avg_roi: float


class SeasonalityTrend(BaseModel):
    """Aggregated release timing seasonality."""

    release_month: int
    month_name: str
    movie_count: int
    avg_revenue: float
    avg_roi: float


class TrendsResponse(BaseModel):
    """Comprehensive trends data for dashboard."""

    genre_trends: List[GenreTrend]
    yearly_trends: List[YearlyTrend]
    seasonality_trends: List[SeasonalityTrend]
    tier_distribution: Dict[str, int]
    headline_kpis: Dict[str, Any]
