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
    RefreshSummary,
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
    Intelligently refresh recommendations for a student

    - Analyzes latest performance data
    - Detects patterns
    - Compares with existing recommendations
    - Generates new/updated AI-powered recommendations
    - Keeps valid recommendations, marks resolved ones
    - Returns summary of changes (new, updated, confirmed, resolved)
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
        result = recommendation_service.generate_recommendations(student_id)

        # Build summary message
        summary = result["summary"]
        message_parts = []
        if summary["new_count"] > 0:
            message_parts.append(f"{summary['new_count']} yeni")
        if summary["updated_count"] > 0:
            message_parts.append(f"{summary['updated_count']} güncellendi")
        if summary["confirmed_count"] > 0:
            message_parts.append(f"{summary['confirmed_count']} onaylandı")
        if summary["resolved_count"] > 0:
            message_parts.append(f"{summary['resolved_count']} çözüldü")

        message = "Öneriler başarıyla güncellendi: " + ", ".join(message_parts) if message_parts else "Öneri değişikliği yok"

        return RecommendationRefreshResponse(
            message=message,
            count=summary["total_active"],
            recommendations=result["recommendations"],
            summary=RefreshSummary(
                new_count=summary["new_count"],
                updated_count=summary["updated_count"],
                confirmed_count=summary["confirmed_count"],
                resolved_count=summary["resolved_count"],
                total_active=summary["total_active"]
            )
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
