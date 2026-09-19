"""
prediction.py (routes)
=======================
POST /predict/static - the only prediction endpoint. Each call runs real
 hand detection + real landmark-model inference on the submitted frame. If the
model isn't trained/loaded yet, this returns 503 - it never fabricates a
prediction.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PredictStaticRequest, PredictStaticResponse
from app.services.predictor import predictor_service
from app.services import analytics as analytics_service

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/static", response_model=PredictStaticResponse)
def predict_static(payload: PredictStaticRequest, db: Session = Depends(get_db)):
    if not predictor_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail=f"Model not trained/loaded yet: {predictor_service.load_error}",
        )

    try:
        result = predictor_service.predict_frame(
            session_id=payload.session_id,
            image_base64=payload.image_base64,
            confidence_threshold=payload.confidence_threshold,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not process frame: {e}")

    # Log every real prediction that produced a class label (not "no hand" / "uncertain")
    if result.get("display") and result["status"] in ("collecting", "held", "confirmed"):
        analytics_service.log_prediction(
            db, payload.session_id, result["display"], result.get("confidence", 0.0)
        )

    return PredictStaticResponse(**result)
