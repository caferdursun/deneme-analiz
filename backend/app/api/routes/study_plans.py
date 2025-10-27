"""
Study Plans API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.study_plan_service import StudyPlanService
from app.schemas.study_plan import (
    StudyPlanGenerateRequest,
    StudyPlanResponse,
    StudyPlanListResponse,
    StudyPlanProgressResponse,
    UpdateItemCompletionRequest,
)
from app.models import Student

router = APIRouter()


@router.post("/generate", response_model=StudyPlanResponse, status_code=status.HTTP_201_CREATED)
async def generate_study_plan(
    request: StudyPlanGenerateRequest,
    db: Session = Depends(get_db),
):
    """
    Generate a new personalized study plan using Claude AI

    - Creates a study plan based on recommendations
    - Uses Claude AI for intelligent scheduling
    - Distributes topics across the time frame
    - Balances subjects and includes review sessions
    """
    study_plan_service = StudyPlanService(db)

    try:
        plan = study_plan_service.generate_study_plan(request)
        return plan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating study plan: {str(e)}"
        )


@router.get("/{plan_id}", response_model=StudyPlanResponse)
async def get_study_plan(
    plan_id: str,
    db: Session = Depends(get_db),
):
    """
    Get a study plan by ID with all days and items
    """
    study_plan_service = StudyPlanService(db)
    plan = study_plan_service.get_study_plan(plan_id)

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan not found"
        )

    return plan


@router.get("/active/current", response_model=StudyPlanResponse)
async def get_active_plan(
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get the currently active study plan for a student
    """
    # Default to first student if not specified
    if not student_id:
        student = db.query(Student).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No student found"
            )
        student_id = student.id

    study_plan_service = StudyPlanService(db)
    plan = study_plan_service.get_active_plan(student_id)

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active study plan found"
        )

    return plan


@router.get("", response_model=StudyPlanListResponse)
async def list_study_plans(
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    List all study plans for a student
    """
    # Default to first student if not specified
    if not student_id:
        student = db.query(Student).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No student found"
            )
        student_id = student.id

    study_plan_service = StudyPlanService(db)
    plans = study_plan_service.get_all_plans(student_id)

    return StudyPlanListResponse(
        plans=plans,
        total=len(plans)
    )


@router.put("/{plan_id}/items/{item_id}/complete", status_code=status.HTTP_200_OK)
async def update_item_completion(
    plan_id: str,
    item_id: str,
    request: UpdateItemCompletionRequest,
    db: Session = Depends(get_db),
):
    """
    Mark a study plan item as complete or incomplete

    - Updates item completion status
    - Automatically updates day completion if all items done
    - Records completion timestamp
    """
    study_plan_service = StudyPlanService(db)
    success = study_plan_service.update_item_completion(item_id, request.completed)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan item not found"
        )

    return {"success": True, "item_id": item_id, "completed": request.completed}


@router.get("/{plan_id}/progress", response_model=StudyPlanProgressResponse)
async def get_plan_progress(
    plan_id: str,
    db: Session = Depends(get_db),
):
    """
    Get progress statistics for a study plan

    - Total and completed items
    - Completion percentage
    - Days remaining
    - On-track status
    """
    study_plan_service = StudyPlanService(db)
    progress = study_plan_service.calculate_progress(plan_id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan not found"
        )

    return progress


@router.put("/{plan_id}/archive", status_code=status.HTTP_200_OK)
async def archive_study_plan(
    plan_id: str,
    db: Session = Depends(get_db),
):
    """
    Archive a study plan (mark as inactive)
    """
    study_plan_service = StudyPlanService(db)
    success = study_plan_service.archive_plan(plan_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan not found"
        )

    return {"success": True, "plan_id": plan_id, "status": "archived"}


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_study_plan(
    plan_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a study plan and all associated days/items
    """
    study_plan_service = StudyPlanService(db)
    success = study_plan_service.delete_plan(plan_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study plan not found"
        )

    return None
