"""
Analytics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    AnalyticsOverview,
    SubjectAnalytics,
    TrendsAnalytics,
)

router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get analytics overview

    - Overall statistics
    - Score trends
    - Top and weak subjects
    """
    analytics_service = AnalyticsService(db)
    overview = analytics_service.get_overview(student_id=student_id)

    return overview


@router.get("/subjects/{subject_name}", response_model=SubjectAnalytics)
async def get_subject_analytics(
    subject_name: str,
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get analytics for a specific subject

    - Subject performance summary
    - Trends over time
    - Related learning outcomes
    """
    analytics_service = AnalyticsService(db)
    subject_analytics = analytics_service.get_subject_analytics(
        subject_name=subject_name,
        student_id=student_id
    )

    if not subject_analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for subject: {subject_name}"
        )

    return subject_analytics


@router.get("/trends", response_model=TrendsAnalytics)
async def get_trends(
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get trends and comparisons

    - Score trends over time
    - Comparison with class/school averages
    - Subject-wise trends
    """
    analytics_service = AnalyticsService(db)
    trends = analytics_service.get_trends(student_id=student_id)

    return trends
