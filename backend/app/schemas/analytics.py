"""
Pydantic schemas for analytics endpoints
"""
from datetime import date
from typing import List, Optional
from pydantic import BaseModel


class OverviewStats(BaseModel):
    """Overall statistics"""
    total_exams: int
    latest_net_score: Optional[float] = None
    average_net_score: Optional[float] = None
    best_score: Optional[float] = None
    worst_score: Optional[float] = None
    total_questions_answered: int
    overall_accuracy: Optional[float] = None


class ScoreTrend(BaseModel):
    """Score trend data point"""
    exam_id: str
    exam_name: str
    exam_date: date
    net_score: float
    net_percentage: float
    class_rank: Optional[int] = None
    school_rank: Optional[int] = None


class SubjectPerformance(BaseModel):
    """Subject performance summary"""
    subject_name: str
    total_exams: int
    average_net: float
    average_percentage: float
    best_net: float
    worst_net: float
    total_questions: int
    total_correct: int
    total_wrong: int
    total_blank: int
    improvement_trend: Optional[str] = None  # "improving", "declining", "stable"


class SubjectTrend(BaseModel):
    """Subject performance over time"""
    exam_id: str
    exam_name: str
    exam_date: date
    subject_name: str
    net_score: float
    net_percentage: float
    correct: int
    wrong: int
    blank: int


class ComparisonData(BaseModel):
    """Comparison with class/school averages"""
    exam_id: str
    exam_name: str
    exam_date: date
    student_net: float
    class_avg: Optional[float] = None
    school_avg: Optional[float] = None
    vs_class_diff: Optional[float] = None
    vs_school_diff: Optional[float] = None


class LearningOutcomeStats(BaseModel):
    """Learning outcome statistics"""
    subject_name: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    outcome_description: Optional[str] = None
    total_appearances: int
    total_questions: int
    total_acquired: int
    average_success_rate: float
    improvement_trend: Optional[str] = None


class AnalyticsOverview(BaseModel):
    """Complete analytics overview"""
    stats: OverviewStats
    score_trends: List[ScoreTrend]
    top_subjects: List[SubjectPerformance]
    weak_subjects: List[SubjectPerformance]


class SubjectAnalytics(BaseModel):
    """Subject-specific analytics"""
    subject_name: str
    performance: SubjectPerformance
    trends: List[SubjectTrend]
    learning_outcomes: List[LearningOutcomeStats]


class TrendsAnalytics(BaseModel):
    """Trends and comparisons"""
    score_trends: List[ScoreTrend]
    comparisons: List[ComparisonData]
    subject_trends: List[SubjectTrend]
