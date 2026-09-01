"""Router for model prediction endpoints."""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.dependencies import get_db, get_inference_service
from backend.app.db.models import Prediction
from backend.app.schemas.predict import PredictRequest, PredictResponse
from backend.app.services.inference_service import InferenceService

router = APIRouter(prefix="/api", tags=["Prediction"])


@router.post("/predict", response_model=PredictResponse, summary="Predict Box Office Revenue & Success Tier")
def predict_revenue(
    request: PredictRequest,
    inference: InferenceService = Depends(get_inference_service),
    db: Session = Depends(get_db),
) -> PredictResponse:
    """Predict a film's box office revenue and success tier from pre-release features.

    Returns the predicted USD revenue, expected ROI, categorical success tier,
    class confidence distribution, and top SHAP positive/negative drivers.
    """
    try:
        response = inference.predict(request)

        # Log prediction to database
        db_pred = Prediction(
            input_payload=request.model_dump_json(),
            predicted_revenue=response.predicted_revenue,
            predicted_roi=response.predicted_roi,
            predicted_tier=response.predicted_tier,
        )
        db.add(db_pred)
        db.commit()

        return response
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
