"""
analytics.py (routes)
======================
GET /analytics, /analytics/predictions, /analytics/classes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AnalyticsSummaryResponse, ClassAnalyticsResponse
from app.services import analytics as analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsSummaryResponse)
def analytics_summary(db: Session = Depends(get_db)):
    summary = analytics_service.get_summary(db)
    return AnalyticsSummaryResponse(**summary)


@router.get("/predictions", response_model=AnalyticsSummaryResponse)
def analytics_predictions(db: Session = Depends(get_db)):
    summary = analytics_service.get_summary(db, limit_recent=50)
    return AnalyticsSummaryResponse(**summary)


@router.get("/classes", response_model=ClassAnalyticsResponse)
def analytics_classes():
    distribution = analytics_service.get_class_distribution()
    return ClassAnalyticsResponse(class_distribution=distribution)
