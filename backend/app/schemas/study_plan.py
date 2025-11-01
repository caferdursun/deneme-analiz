"""
Pydantic schemas for Study Plan
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


# ============ Request Schemas ============

class StudyPlanGenerateRequest(BaseModel):
    """Request schema for generating a new study plan"""

    name: str = Field(..., description="Name of the study plan", min_length=1, max_length=255)
    time_frame: int = Field(..., description="Duration in days (7, 14, or 30)", ge=7, le=30)
    daily_study_time: int = Field(..., description="Minutes per day", ge=30, le=480)
    study_style: str = Field(..., description="Study style: intensive, balanced, or relaxed")
    recommendation_ids: List[str] = Field(default=[], description="List of recommendation IDs to include in the plan")
    student_id: Optional[str] = Field(None, description="Student ID (optional, defaults to first student)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "2 Haftalık Matematik Yoğunlaşma Planı",
                "time_frame": 14,
                "daily_study_time": 180,
                "study_style": "balanced",
                "recommendation_ids": ["rec-id-1", "rec-id-2"],
            }
        }


# ============ Response Schemas ============

class StudyPlanItemResponse(BaseModel):
    """Study plan item (task) response"""

    id: str
    day_id: str
    recommendation_id: Optional[str]
    subject_name: str
    topic: str
    duration_minutes: int
    order: int
    completed: bool
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class StudyPlanDayResponse(BaseModel):
    """Study plan day response"""

    id: str
    plan_id: str
    day_number: int
    date: date
    total_duration_minutes: int
    completed: bool
    notes: Optional[str]
    items: List[StudyPlanItemResponse] = []

    class Config:
        from_attributes = True


class StudyPlanResponse(BaseModel):
    """Study plan response"""

    id: str
    student_id: str
    name: str
    time_frame: int
    daily_study_time: int
    study_style: str
    status: str
    start_date: date
    end_date: date
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    days: List[StudyPlanDayResponse] = []

    class Config:
        from_attributes = True


class StudyPlanListResponse(BaseModel):
    """List of study plans response"""

    plans: List[StudyPlanResponse]
    total: int


class StudyPlanProgressResponse(BaseModel):
    """Study plan progress stats"""

    plan_id: str
    total_items: int
    completed_items: int
    completion_percentage: float
    total_days: int
    completed_days: int
    days_remaining: int
    on_track: bool  # Are we on schedule?


# ============ Update Schemas ============

class UpdateItemCompletionRequest(BaseModel):
    """Request to mark an item as complete/incomplete"""

    completed: bool


class UpdateDayNotesRequest(BaseModel):
    """Request to update day notes"""

    notes: str
