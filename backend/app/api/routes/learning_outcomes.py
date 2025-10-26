"""
Learning Outcomes API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from app.core.database import get_db
from app.services.learning_outcome_cleanup_service import LearningOutcomeCleanupService

router = APIRouter(prefix="/learning-outcomes", tags=["learning-outcomes"])


@router.get("/analyze")
async def analyze_outcomes(
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Analyze learning outcomes for similarity using Claude AI

    Returns similarity groups with confidence scores
    """
    service = LearningOutcomeCleanupService(db)

    try:
        result = service.analyze_outcomes(student_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/cleanup")
async def cleanup_outcomes(
    merge_groups: List[Dict[str, Any]] = Body(...),
    merged_by: str = Body(default="user"),
    db: Session = Depends(get_db)
):
    """
    Perform merge operations for approved similarity groups

    Body format:
    {
        "merge_groups": [
            {
                "group_id": "...",
                "outcome_ids": ["id1", "id2"],
                "suggested_name": "...",
                "confidence_score": 95,
                "reason": "..."
            }
        ],
        "merged_by": "user"
    }
    """
    service = LearningOutcomeCleanupService(db)

    try:
        result = service.perform_merge(merge_groups, merged_by)
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.post("/undo/{merge_group_id}")
async def undo_merge(
    merge_group_id: str,
    undone_by: str = Body(default="user", embed=True),
    db: Session = Depends(get_db)
):
    """
    Undo a merge operation by restoring original outcomes
    """
    service = LearningOutcomeCleanupService(db)

    try:
        result = service.undo_merge(merge_group_id, undone_by)

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("error", "Merge not found"))

        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Undo failed: {str(e)}")


@router.get("/merge-history")
async def get_merge_history(
    limit: int = Query(50, ge=1, le=200),
    include_undone: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get recent merge operations
    """
    service = LearningOutcomeCleanupService(db)

    try:
        history = service.get_merge_history(limit, include_undone)
        return {
            "history": history,
            "total": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")
