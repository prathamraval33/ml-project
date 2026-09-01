"""Router for Trends and Big Data aggregate analytics."""

import calendar
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from backend.app.dependencies import get_db
from backend.app.db.models import Movie
from backend.app.schemas.movie import (
    GenreTrend,
    SeasonalityTrend,
    TrendsResponse,
    YearlyTrend,
)
from backend.app.services.cache_service import cache_service

router = APIRouter(prefix="/api/trends", tags=["Trends"])


@router.get("", response_model=TrendsResponse, summary="Get Aggregate Trend Analytics")
def get_trends(db: Session = Depends(get_db)) -> TrendsResponse:
    """Compute aggregate film revenue, budget, and ROI trends across genres, release years, and seasonality."""
    cache_key = "trends:aggregated_summary"
    cached = cache_service.get(cache_key)
    if cached:
        return TrendsResponse(**cached)

    # 1. Headline KPIs
    total_movies = db.query(func.count(Movie.id)).scalar() or 0
    total_box_office = db.query(func.sum(Movie.revenue)).scalar() or 0.0
    avg_budget = db.query(func.avg(Movie.budget)).scalar() or 0.0
    avg_roi = db.query(func.avg(Movie.roi)).scalar() or 0.0

    hit_count = db.query(func.count(Movie.id)).filter(Movie.success_tier.in_(["Hit", "Blockbuster"])).scalar() or 0
    hit_rate = (hit_count / total_movies * 100.0) if total_movies > 0 else 0.0

    headline_kpis = {
        "total_catalog_size": total_movies,
        "total_box_office_usd": round(total_box_office, 2),
        "average_budget_usd": round(avg_budget, 2),
        "average_roi": round(avg_roi, 2),
        "hit_rate_percent": round(hit_rate, 2),
    }

    # 2. Genre Trends
    genre_rows = (
        db.query(
            Movie.primary_genre,
            func.count(Movie.id).label("count"),
            func.avg(Movie.budget).label("avg_budget"),
            func.avg(Movie.revenue).label("avg_revenue"),
            func.avg(Movie.roi).label("avg_roi"),
            func.sum(case((Movie.success_tier.in_(["Hit", "Blockbuster"]), 1), else_=0)).label("hits"),
        )
        .filter(Movie.primary_genre.isnot(None))
        .group_by(Movie.primary_genre)
        .order_by(func.count(Movie.id).desc())
        .limit(15)
        .all()
    )

    genre_trends: List[GenreTrend] = []
    for r in genre_rows:
        count = r.count or 1
        hits = r.hits or 0
        genre_trends.append(
            GenreTrend(
                genre=r.primary_genre,
                movie_count=count,
                avg_budget=round(float(r.avg_budget or 0), 2),
                avg_revenue=round(float(r.avg_revenue or 0), 2),
                avg_roi=round(float(r.avg_roi or 0), 2),
                hit_rate_percent=round((hits / count) * 100.0, 2),
            )
        )

    # 3. Yearly Trends
    yearly_rows = (
        db.query(
            Movie.release_year,
            func.count(Movie.id).label("count"),
            func.sum(Movie.revenue).label("total_rev"),
            func.avg(Movie.revenue).label("avg_rev"),
            func.avg(Movie.budget).label("avg_bud"),
            func.avg(Movie.roi).label("avg_roi"),
        )
        .filter(Movie.release_year.isnot(None), Movie.release_year >= 1990)
        .group_by(Movie.release_year)
        .order_by(Movie.release_year.asc())
        .all()
    )

    yearly_trends: List[YearlyTrend] = [
        YearlyTrend(
            release_year=r.release_year,
            movie_count=r.count,
            total_revenue=round(float(r.total_rev or 0), 2),
            avg_revenue=round(float(r.avg_rev or 0), 2),
            avg_budget=round(float(r.avg_bud or 0), 2),
            avg_roi=round(float(r.avg_roi or 0), 2),
        )
        for r in yearly_rows
    ]

    # 4. Seasonality Trends (By Month)
    season_rows = (
        db.query(
            Movie.release_month,
            func.count(Movie.id).label("count"),
            func.avg(Movie.revenue).label("avg_rev"),
            func.avg(Movie.roi).label("avg_roi"),
        )
        .filter(Movie.release_month.isnot(None))
        .group_by(Movie.release_month)
        .order_by(Movie.release_month.asc())
        .all()
    )

    seasonality_trends: List[SeasonalityTrend] = [
        SeasonalityTrend(
            release_month=r.release_month,
            month_name=calendar.month_abbr[r.release_month],
            movie_count=r.count,
            avg_revenue=round(float(r.avg_rev or 0), 2),
            avg_roi=round(float(r.avg_roi or 0), 2),
        )
        for r in season_rows
        if 1 <= r.release_month <= 12
    ]

    # 5. Tier Distribution
    tier_rows = (
        db.query(Movie.success_tier, func.count(Movie.id))
        .group_by(Movie.success_tier)
        .all()
    )
    tier_distribution = {tier: count for tier, count in tier_rows if tier}

    response_data = TrendsResponse(
        genre_trends=genre_trends,
        yearly_trends=yearly_trends,
        seasonality_trends=seasonality_trends,
        tier_distribution=tier_distribution,
        headline_kpis=headline_kpis,
    )

    cache_service.set(cache_key, response_data.model_dump(), expire_seconds=3600)
    return response_data
