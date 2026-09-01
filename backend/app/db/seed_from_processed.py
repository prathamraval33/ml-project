"""Database seeding script from processed parquet datasets.

Creates tables, runs batch inference for historical films, and seeds
the database with rich actual and predicted metadata.
"""

import json
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.db.base import Base, engine, SessionLocal
from backend.app.db.models import Movie
from backend.app.services.inference_service import inference_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def seed_database() -> int:
    """Seed database with movies from train and test parquet files."""
    logger.info("Creating database tables if not present...")
    Base.metadata.create_all(bind=engine)

    processed_dir = Path(settings.PROCESSED_DATA_DIR)
    train_path = processed_dir / "train.parquet"
    test_path = processed_dir / "test.parquet"

    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError("Processed parquet files missing. Run feature engineering first.")

    train_df = pd.read_parquet(train_path)
    train_df["split"] = "train"
    test_df = pd.read_parquet(test_path)
    test_df["split"] = "test"

    combined_df = pd.concat([train_df, test_df], ignore_index=True)
    logger.info("Loaded %d total processed records (Train: %d, Test: %d)", len(combined_df), len(train_df), len(test_df))

    # Run batch inference with champion regressor and classifier
    features = inference_service.reg_features
    X_features = combined_df[features].fillna(0)

    pred_log_revenue = inference_service.regressor.predict(X_features)
    pred_revenue = np.expm1(np.clip(pred_log_revenue, 0, 30))

    pred_cls_proba = inference_service.classifier.predict_proba(X_features)
    pred_cls_idx = np.argmax(pred_cls_proba, axis=1)
    pred_tiers = inference_service.label_encoder.inverse_transform(pred_cls_idx)

    combined_df["predicted_revenue"] = pred_revenue
    combined_df["predicted_roi"] = (pred_revenue - combined_df["budget"]) / combined_df["budget"].replace(0, 1)
    combined_df["predicted_tier"] = pred_tiers

    db: Session = SessionLocal()
    try:
        # Clear existing movies for clean seeding
        db.query(Movie).delete()
        db.commit()

        movies_to_insert = []
        for _, row in combined_df.iterrows():
            movie_obj = Movie(
                id=int(row["id"]),
                title=str(row.get("title", f"Movie {row['id']}")),
                budget=float(row.get("budget", 0.0)),
                revenue=float(row.get("revenue", 0.0)),
                runtime=int(row.get("runtime", 0)) if pd.notnull(row.get("runtime")) else None,
                release_date=str(row.get("release_date", "")) if pd.notnull(row.get("release_date")) else None,
                release_year=int(row.get("release_year", 0)) if pd.notnull(row.get("release_year")) else None,
                release_month=int(row.get("release_month", 0)) if pd.notnull(row.get("release_month")) else None,
                genres=json.dumps(row["genres"].tolist()) if isinstance(row.get("genres"), (list, np.ndarray)) else str(row.get("genres", "")),
                primary_genre=str(row.get("primary_genre", "Drama")) if pd.notnull(row.get("primary_genre")) else "Drama",
                director=str(row.get("director", "Unknown")) if pd.notnull(row.get("director")) else "Unknown",
                production_companies=json.dumps(row["production_companies"].tolist()) if isinstance(row.get("production_companies"), (list, np.ndarray)) else str(row.get("production_companies", "")),
                production_countries=json.dumps(row["production_countries"].tolist()) if isinstance(row.get("production_countries"), (list, np.ndarray)) else str(row.get("production_countries", "")),
                cast=json.dumps(row["cast"].tolist()) if isinstance(row.get("cast"), (list, np.ndarray)) else str(row.get("cast", "")),
                original_language=str(row.get("original_language", "en")) if pd.notnull(row.get("original_language")) else "en",
                popularity=float(row.get("popularity", 0.0)) if pd.notnull(row.get("popularity")) else None,
                vote_average=float(row.get("vote_average", 0.0)) if pd.notnull(row.get("vote_average")) else None,
                vote_count=int(row.get("vote_count", 0)) if pd.notnull(row.get("vote_count")) else None,
                is_franchise=int(row.get("is_franchise", 0)),
                is_holiday_release=int(row.get("is_holiday_release", 0)),
                roi=float(row.get("roi", 0.0)) if pd.notnull(row.get("roi")) else None,
                success_tier=str(row.get("success_tier", "Flop")) if pd.notnull(row.get("success_tier")) else "Flop",
                predicted_revenue=round(float(row.get("predicted_revenue", 0.0)), 2),
                predicted_roi=round(float(row.get("predicted_roi", 0.0)), 4),
                predicted_tier=str(row.get("predicted_tier", "Flop")),
                split=str(row.get("split", "train")),
            )
            movies_to_insert.append(movie_obj)

        db.bulk_save_objects(movies_to_insert)
        db.commit()
        logger.info("Successfully seeded %d movies into database.", len(movies_to_insert))
        return len(movies_to_insert)
    except Exception as e:
        db.rollback()
        logger.error("Error seeding database: %s", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
