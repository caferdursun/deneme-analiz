"""
Pydantic schemas for exam-related endpoints
"""
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# Student schemas
class StudentBase(BaseModel):
    name: str
    school: Optional[str] = None
    grade: Optional[str] = None
    class_section: Optional[str] = None


class StudentResponse(StudentBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Exam schemas
class ExamBase(BaseModel):
    exam_name: str
    exam_date: date
    booklet_type: Optional[str] = None


class ExamResponse(ExamBase):
    id: str
    student_id: str
    pdf_path: Optional[str] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Exam Result schemas
class ExamResultResponse(BaseModel):
    total_questions: int
    total_correct: int
    total_wrong: int
    total_blank: int
    net_score: float
    net_percentage: float
    class_rank: Optional[int] = None
    class_total: Optional[int] = None
    school_rank: Optional[int] = None
    school_total: Optional[int] = None
    class_avg: Optional[float] = None
    school_avg: Optional[float] = None

    class Config:
        from_attributes = True


# Subject Result schemas
class SubjectResultResponse(BaseModel):
    id: str
    subject_name: str
    total_questions: int
    correct: int
    wrong: int
    blank: int
    net_score: float
    net_percentage: float
    class_rank: Optional[int] = None
    class_avg: Optional[float] = None
    school_rank: Optional[int] = None
    school_avg: Optional[float] = None

    class Config:
        from_attributes = True


# Learning Outcome schemas
class LearningOutcomeResponse(BaseModel):
    id: str
    subject_name: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    outcome_description: Optional[str] = None
    total_questions: int
    acquired: int
    lost: int
    success_rate: Optional[float] = None
    student_percentage: Optional[float] = None
    class_percentage: Optional[float] = None
    school_percentage: Optional[float] = None

    class Config:
        from_attributes = True


# Question schemas
class QuestionResponse(BaseModel):
    id: str
    subject_name: str
    question_number: int
    correct_answer: Optional[str] = None
    student_answer: Optional[str] = None
    is_correct: bool
    is_blank: bool
    is_canceled: bool

    class Config:
        from_attributes = True


# Complete exam detail response
class ExamDetailResponse(BaseModel):
    exam: ExamResponse
    student: StudentResponse
    overall_result: Optional[ExamResultResponse] = None
    subject_results: List[SubjectResultResponse] = []
    learning_outcomes: List[LearningOutcomeResponse] = []
    questions: List[QuestionResponse] = []


# Upload response
class ExamUploadResponse(BaseModel):
    exam_id: str
    message: str
    status: str


# Exam list response
class ExamListResponse(BaseModel):
    exams: List[ExamResponse]
    total: int
