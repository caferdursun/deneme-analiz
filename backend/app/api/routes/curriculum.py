"""
Curriculum API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.curriculum_service import CurriculumService
from app.schemas.curriculum import (
    CurriculumFullResponse,
    CurriculumGradeResponse,
    CurriculumSubjectResponse,
)

router = APIRouter()


@router.get("/", response_model=CurriculumFullResponse)
async def get_all_curriculum(db: Session = Depends(get_db)):
    """
    Get the complete high school curriculum

    Returns curriculum organized by:
    - Subject (Türkçe, Matematik, Fizik, etc.) - Top level
    - Grade (9, 10, 11, 12) - Within each subject
    - Unit (Üniteler) - Within each grade
    - Topics (Konular) - Within each unit

    Subjects are ordered with Türkçe, Matematik, and Sciences at the top.
    """
    service = CurriculumService(db)
    return service.get_all_curriculum()


@router.get("/subject/{subject_name}", response_model=CurriculumSubjectResponse)
async def get_subject_by_name(
    subject_name: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific subject with all its grades, units, and topics

    Args:
        subject_name: Name of the subject (e.g., "Matematik", "Fizik")

    Returns detailed curriculum for that subject across all grade levels.
    """
    service = CurriculumService(db)
    subject = service.get_subject_by_name(subject_name)

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject '{subject_name}' not found"
        )

    return subject


@router.get("/search")
async def search_topics(
    q: str = Query(..., min_length=2, description="Search query"),
    grade: Optional[str] = Query(None, description="Filter by grade"),
    db: Session = Depends(get_db)
):
    """
    Search for topics by keyword

    Args:
        q: Search query (minimum 2 characters)
        grade: Optional grade filter (9, 10, 11, or 12)

    Returns matching topics with their context (grade, subject, unit).
    """
    if grade and grade not in ["9", "10", "11", "12"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grade must be 9, 10, 11, or 12"
        )

    service = CurriculumService(db)
    results = service.search_topics(q, grade)

    return {
        "query": q,
        "grade_filter": grade,
        "results": results,
        "total": len(results)
    }


@router.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get curriculum statistics

    Returns counts of subjects, units, and topics by grade.
    """
    service = CurriculumService(db)
    return service.get_statistics()
