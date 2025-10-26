"""
Database models
"""
from app.models.student import Student
from app.models.exam import Exam
from app.models.exam_result import ExamResult
from app.models.subject_result import SubjectResult
from app.models.learning_outcome import LearningOutcome
from app.models.question import Question
from app.models.recommendation import Recommendation
from app.models.outcome_merge_history import OutcomeMergeHistory

__all__ = [
    "Student",
    "Exam",
    "ExamResult",
    "SubjectResult",
    "LearningOutcome",
    "Question",
    "Recommendation",
    "OutcomeMergeHistory",
]