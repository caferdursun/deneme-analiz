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
from app.models.study_plan import StudyPlan
from app.models.study_plan_day import StudyPlanDay
from app.models.study_plan_item import StudyPlanItem
from app.models.resource import Resource
from app.models.recommendation_resource import RecommendationResource
from app.models.resource_blacklist import ResourceBlacklist

__all__ = [
    "Student",
    "Exam",
    "ExamResult",
    "SubjectResult",
    "LearningOutcome",
    "Question",
    "Recommendation",
    "OutcomeMergeHistory",
    "StudyPlan",
    "StudyPlanDay",
    "StudyPlanItem",
    "Resource",
    "RecommendationResource",
    "ResourceBlacklist",
]