"""Router for Movie catalog browsing, filtering, and detail endpoints."""

import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from backend.app.dependencies import get_db
from backend.app.db.models import Movie
from backend.app.schemas.movie import MovieDetail, MovieListResponse

router = APIRouter(prefix="/api/movies", tags=["Movies"])


@router.get("", response_model=MovieListResponse, summary="List & Filter Movies")
def list_movies(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search title or director"),
    genre: Optional[str] = Query(default=None, description="Filter by primary genre"),
    tier: Optional[str] = Query(default=None, description="Filter by success tier"),
    min_year: Optional[int] = Query(default=None, description="Minimum release year"),
    max_year: Optional[int] = Query(default=None, description="Maximum release year"),
    split: Optional[str] = Query(default=None, description="Filter by split (train/test)"),
    sort_by: str = Query(default="revenue", description="Field to sort by (revenue, budget, roi, predicted_revenue)"),
    order: str = Query(default="desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
) -> MovieListResponse:
    """Retrieve paginated and filterable movie records with actual vs predicted financials."""
    query = db.query(Movie)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Movie.title.ilike(search_pattern)) | (Movie.director.ilike(search_pattern))
        )

    if genre:
        query = query.filter(Movie.primary_genre.ilike(f"%{genre}%"))

    if tier:
        query = query.filter(Movie.success_tier == tier)

    if min_year:
        query = query.filter(Movie.release_year >= min_year)

    if max_year:
        query = query.filter(Movie.release_year <= max_year)

    if split:
        query = query.filter(Movie.split == split)

    # Sorting
    sort_column = getattr(Movie, sort_by, Movie.revenue)
    if order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    total_pages = max(1, (total + size - 1) // size)

    return MovieListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
    )


@router.get("/{movie_id}", response_model=MovieDetail, summary="Get Movie Details")
def get_movie_detail(
    movie_id: int,
    db: Session = Depends(get_db),
) -> MovieDetail:
    """Get single movie record by ID."""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found.")
    return movie
