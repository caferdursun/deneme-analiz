"""
Pydantic schemas for Curriculum
New hierarchy: Subject (Ders) -> Grade (Sınıf) -> Unit (Ünite) -> Topic (Konu)
"""
from pydantic import BaseModel
from typing import List
from datetime import datetime


# ============ Response Schemas ============

class CurriculumTopicResponse(BaseModel):
    """Curriculum topic response (4th level: Konu)"""

    id: str
    unit_id: str
    topic_name: str
    order: int

    class Config:
        from_attributes = True


class CurriculumUnitResponse(BaseModel):
    """Curriculum unit response (3rd level: Ünite)"""

    id: str
    grade_id: str
    unit_no: int
    unit_name: str
    topics: List[CurriculumTopicResponse] = []

    class Config:
        from_attributes = True


class CurriculumGradeResponse(BaseModel):
    """Curriculum grade response (2nd level: Sınıf)"""

    id: str
    subject_id: str
    grade: str
    units: List[CurriculumUnitResponse] = []

    class Config:
        from_attributes = True


class CurriculumSubjectResponse(BaseModel):
    """Curriculum subject response (1st level: Ders)"""

    id: str
    subject_name: str
    order: int
    grades: List[CurriculumGradeResponse] = []

    class Config:
        from_attributes = True


class CurriculumFullResponse(BaseModel):
    """Full curriculum response with all subjects"""

    subjects: List[CurriculumSubjectResponse]
    total_subjects: int
    total_units: int
    total_topics: int
