"""Router for What-If simulation and sensitivity analysis."""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.dependencies import get_db, get_inference_service
from backend.app.db.models import Movie, WhatIfSession
from backend.app.schemas.predict import PredictRequest, WhatIfRequest, WhatIfResponse
from backend.app.services.inference_service import InferenceService

router = APIRouter(prefix="/api", tags=["What-If Simulator"])


@router.post("/whatif", response_model=WhatIfResponse, summary="Simulate What-If Parameter Changes")
def simulate_whatif(
    request: WhatIfRequest,
    inference: InferenceService = Depends(get_inference_service),
    db: Session = Depends(get_db),
) -> WhatIfResponse:
    """Run dynamic parameter sensitivity simulation.

    Compares baseline parameters against user adjustments (e.g. higher budget,
    different genres, new release window) and returns revenue/ROI deltas.
    """
    try:
        # If a base movie ID was supplied and no explicit base_params given, load from DB
        if request.base_movie_id and not request.base_params:
            movie = db.query(Movie).filter(Movie.id == request.base_movie_id).first()
            if movie:
                import json as pyjson
                try:
                    genres_list = pyjson.loads(movie.genres) if movie.genres and movie.genres.startswith("[") else [movie.primary_genre or "Drama"]
                except Exception:
                    genres_list = [movie.primary_genre or "Drama"]

                request.base_params = PredictRequest(
                    title=movie.title,
                    budget=movie.budget if movie.budget > 0 else 25_000_000.0,
                    runtime=movie.runtime or 110,
                    genres=genres_list,
                    release_date=movie.release_date or "2026-07-15",
                    director=movie.director or "Unknown",
                    is_franchise=movie.is_franchise or 0,
                )

        response = inference.whatif_simulate(request)

        # Record simulation session
        session_record = WhatIfSession(
            base_movie_id=request.base_movie_id,
            base_budget=response.base_budget,
            modified_budget=response.modified_budget,
            base_predicted_revenue=response.base_predicted_revenue,
            modified_predicted_revenue=response.modified_predicted_revenue,
            revenue_delta=response.revenue_delta,
            roi_delta=response.roi_delta,
            adjustments_json=json.dumps(request.adjustments),
        )
        db.add(session_record)
        db.commit()

        return response
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"What-If simulation failed: {str(e)}")
