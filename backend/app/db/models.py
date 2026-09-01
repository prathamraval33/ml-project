"""SQLAlchemy ORM models for CineForecast."""

from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.app.db.base import Base


class Movie(Base):
    """Movie entity storing raw metadata, actual box office results, and model predictions."""

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512), index=True, nullable=False)
    budget = Column(Float, nullable=False, default=0.0)
    revenue = Column(Float, nullable=False, default=0.0)
    runtime = Column(Integer, nullable=True)
    release_date = Column(String(32), index=True, nullable=True)
    release_year = Column(Integer, index=True, nullable=True)
    release_month = Column(Integer, nullable=True)
    genres = Column(Text, nullable=True)  # JSON or comma-separated string
    primary_genre = Column(String(128), index=True, nullable=True)
    director = Column(String(256), index=True, nullable=True)
    production_companies = Column(Text, nullable=True)
    production_countries = Column(Text, nullable=True)
    cast = Column(Text, nullable=True)
    original_language = Column(String(16), nullable=True)
    popularity = Column(Float, nullable=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=True)
    is_franchise = Column(Integer, default=0)
    is_holiday_release = Column(Integer, default=0)
    
    # Financial analytics
    roi = Column(Float, nullable=True)
    success_tier = Column(String(32), index=True, nullable=True)  # Flop, Break-even, Hit, Blockbuster
    
    # Model predictions
    predicted_revenue = Column(Float, nullable=True)
    predicted_roi = Column(Float, nullable=True)
    predicted_tier = Column(String(32), nullable=True)
    split = Column(String(16), default="train")  # train or test

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="movie", cascade="all, delete-orphan")


class Prediction(Base):
    """Historical record of model inference requests."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="SET NULL"), nullable=True)
    input_payload = Column(Text, nullable=False)  # JSON string of input features
    predicted_revenue = Column(Float, nullable=False)
    predicted_roi = Column(Float, nullable=True)
    predicted_tier = Column(String(32), nullable=True)
    model_version = Column(String(64), default="xgb_champion_v1")
    created_at = Column(DateTime, default=datetime.utcnow)

    movie = relationship("Movie", back_populates="predictions")


class WhatIfSession(Base):
    """Record of interactive what-if simulations run by users."""

    __tablename__ = "whatif_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    base_movie_id = Column(Integer, ForeignKey("movies.id", ondelete="SET NULL"), nullable=True)
    base_budget = Column(Float, nullable=False)
    modified_budget = Column(Float, nullable=False)
    base_predicted_revenue = Column(Float, nullable=False)
    modified_predicted_revenue = Column(Float, nullable=False)
    revenue_delta = Column(Float, nullable=False)
    roi_delta = Column(Float, nullable=False)
    adjustments_json = Column(Text, nullable=False)  # JSON representation of tweaks
    created_at = Column(DateTime, default=datetime.utcnow)
