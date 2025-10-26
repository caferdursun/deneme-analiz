"""
Recommendations API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import (
    RecommendationsListResponse,
    RecommendationResponse,
    RecommendationRefreshResponse,
)

router = APIRouter()


@router.get("", response_model=RecommendationsListResponse)
async def get_recommendations(
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get active recommendations for a student

    - Returns recommendations ordered by priority
    - Filters by student_id if provided
    """
    # For MVP, we'll use the first student if not specified
    if not student_id:
        from app.models import Student
        student = db.query(Student).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No student found"
            )
        student_id = student.id

    recommendation_service = RecommendationService(db)
    recommendations = recommendation_service.get_active_recommendations(student_id)

    return RecommendationsListResponse(
        recommendations=recommendations,
        total=len(recommendations)
    )


@router.post("/refresh", response_model=RecommendationRefreshResponse)
async def refresh_recommendations(
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Regenerate recommendations for a student

    - Analyzes latest performance data
    - Detects patterns
    - Generates new AI-powered recommendations
    - Replaces old active recommendations
    """
    # For MVP, we'll use the first student if not specified
    if not student_id:
        from app.models import Student
        student = db.query(Student).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No student found"
            )
        student_id = student.id

    recommendation_service = RecommendationService(db)

    try:
        recommendations = recommendation_service.generate_recommendations(student_id)

        return RecommendationRefreshResponse(
            message="Recommendations generated successfully",
            count=len(recommendations),
            recommendations=recommendations
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.post("/{recommendation_id}/complete", response_model=dict)
async def mark_recommendation_complete(
    recommendation_id: str,
    db: Session = Depends(get_db),
):
    """
    Mark a recommendation as completed

    - Sets is_active to False
    - Recommendation will not appear in active list
    """
    recommendation_service = RecommendationService(db)

    success = recommendation_service.mark_as_completed(recommendation_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation with id {recommendation_id} not found"
        )

    return {"message": "Recommendation marked as completed", "id": recommendation_id}
