"""
Pydantic schemas for Curriculum
New hierarchy: ExamType (Sınav Türü) -> Subject (Ders) -> Topic (Konu)
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ============ Response Schemas ============

class TopicResponse(BaseModel):
    """Topic response (3rd level: Konu)"""

    id: str
    subject_id: str
    name: str
    grade_info: Optional[str] = None  # e.g., "9", "9,10", "9,10,11"
    order: int
    created_at: datetime

    class Config:
        from_attributes = True


class SubjectResponse(BaseModel):
    """Subject response (2nd level: Ders)"""

    id: str
    exam_type_id: str
    name: str
    order: int
    created_at: datetime
    topics: List[TopicResponse] = []

    class Config:
        from_attributes = True


class ExamTypeResponse(BaseModel):
    """ExamType response (1st level: Sınav Türü)"""

    id: str
    name: str
    display_name: str
    order: int
    created_at: datetime
    subjects: List[SubjectResponse] = []

    class Config:
        from_attributes = True


class CurriculumFullResponse(BaseModel):
    """Full curriculum response with all exam types"""

    exam_types: List[ExamTypeResponse]
    total_exam_types: int
    total_subjects: int
    total_topics: int


# ============ Summary Schemas (for compact views) ============

class TopicSummary(BaseModel):
    """Topic summary without relationships"""

    id: str
    name: str
    grade_info: Optional[str] = None

    class Config:
        from_attributes = True


class SubjectSummary(BaseModel):
    """Subject summary with topic count"""

    id: str
    name: str
    topic_count: int

    class Config:
        from_attributes = True


class ExamTypeSummary(BaseModel):
    """ExamType summary with subject and topic counts"""

    id: str
    name: str
    display_name: str
    subject_count: int
    topic_count: int

    class Config:
        from_attributes = True
