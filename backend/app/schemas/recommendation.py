"""
Pydantic schemas for recommendations
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RecommendationBase(BaseModel):
    """Base recommendation schema"""
    priority: int
    subject_name: Optional[str] = None
    topic: Optional[str] = None
    issue_type: str
    description: str
    action_items: List[str]
    rationale: Optional[str] = None
    impact_score: Optional[float] = None
    learning_outcome_ids: Optional[List[str]] = None  # Links to specific learning outcomes


class RecommendationCreate(RecommendationBase):
    """Schema for creating a recommendation"""
    student_id: str


class RecommendationResponse(RecommendationBase):
    """Schema for recommendation response"""
    id: str
    student_id: str
    generated_at: datetime
    is_active: bool
    created_at: datetime

    # New tracking fields
    status: str  # 'new', 'active', 'updated', 'resolved', 'superseded'
    last_confirmed_at: Optional[datetime] = None
    previous_recommendation_id: Optional[str] = None

    class Config:
        from_attributes = True


class RecommendationsListResponse(BaseModel):
    """Schema for list of recommendations"""
    recommendations: List[RecommendationResponse]
    total: int


class RecommendationRefreshRequest(BaseModel):
    """Schema for refresh request"""
    student_id: Optional[str] = None


class RefreshSummary(BaseModel):
    """Summary of changes during refresh"""
    new_count: int  # Brand new recommendations
    updated_count: int  # Updated versions of existing recommendations
    confirmed_count: int  # Existing recommendations still valid
    resolved_count: int  # Issues that are no longer present
    total_active: int  # Total active recommendations after refresh


class RecommendationRefreshResponse(BaseModel):
    """Schema for refresh response"""
    message: str
    count: int
    recommendations: List[RecommendationResponse]
    summary: RefreshSummary  # Detailed change summary
