"""
Analytics service for calculating statistics and trends
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime

from app.models import Exam, ExamResult, SubjectResult, LearningOutcome
from app.schemas.analytics import (
    OverviewStats,
    ScoreTrend,
    SubjectPerformance,
    SubjectTrend,
    ComparisonData,
    LearningOutcomeStats,
    AnalyticsOverview,
    SubjectAnalytics,
    TrendsAnalytics,
)


class AnalyticsService:
    """Service for analytics calculations"""

    def __init__(self, db: Session):
        self.db = db

    def get_overview(self, student_id: Optional[str] = None) -> AnalyticsOverview:
        """Get complete analytics overview"""

        # Build base query
        query = self.db.query(Exam)
        if student_id:
            query = query.filter(Exam.student_id == student_id)

        exams = query.order_by(Exam.exam_date.desc()).all()

        if not exams:
            return AnalyticsOverview(
                stats=OverviewStats(
                    total_exams=0,
                    total_questions_answered=0
                ),
                score_trends=[],
                top_subjects=[],
                weak_subjects=[]
            )

        # Calculate overall stats
        stats = self._calculate_overall_stats(exams)

        # Get score trends
        score_trends = self._get_score_trends(exams)

        # Get subject performance
        all_subjects = self._get_all_subject_performance(exams)

        # Sort subjects by performance
        sorted_subjects = sorted(all_subjects, key=lambda x: x.average_percentage, reverse=True)
        top_subjects = sorted_subjects[:3]
        weak_subjects = sorted_subjects[-3:]

        return AnalyticsOverview(
            stats=stats,
            score_trends=score_trends,
            top_subjects=top_subjects,
            weak_subjects=weak_subjects
        )

    def get_subject_analytics(
        self,
        subject_name: str,
        student_id: Optional[str] = None
    ) -> Optional[SubjectAnalytics]:
        """Get analytics for a specific subject"""

        # Build query
        query = self.db.query(Exam)
        if student_id:
            query = query.filter(Exam.student_id == student_id)

        exams = query.order_by(Exam.exam_date).all()

        if not exams:
            return None

        # Get subject results
        subject_results = []
        for exam in exams:
            for sr in exam.subject_results:
                if sr.subject_name == subject_name:
                    subject_results.append((exam, sr))

        if not subject_results:
            return None

        # Calculate performance
        performance = self._calculate_subject_performance(subject_name, subject_results)

        # Get trends
        trends = self._get_subject_trends(subject_results)

        # Get learning outcomes
        learning_outcomes = self._get_learning_outcome_stats(exams, subject_name)

        return SubjectAnalytics(
            subject_name=subject_name,
            performance=performance,
            trends=trends,
            learning_outcomes=learning_outcomes
        )

    def get_trends(self, student_id: Optional[str] = None) -> TrendsAnalytics:
        """Get trends and comparisons"""

        query = self.db.query(Exam)
        if student_id:
            query = query.filter(Exam.student_id == student_id)

        exams = query.order_by(Exam.exam_date).all()

        # Get score trends
        score_trends = self._get_score_trends(exams)

        # Get comparisons
        comparisons = self._get_comparisons(exams)

        # Get all subject trends
        subject_trends = []
        subjects = set()
        for exam in exams:
            for sr in exam.subject_results:
                subjects.add(sr.subject_name)

        for subject in subjects:
            for exam in exams:
                for sr in exam.subject_results:
                    if sr.subject_name == subject:
                        subject_trends.append(SubjectTrend(
                            exam_id=exam.id,
                            exam_name=exam.exam_name,
                            exam_date=exam.exam_date,
                            subject_name=sr.subject_name,
                            net_score=sr.net_score,
                            net_percentage=sr.net_percentage,
                            correct=sr.correct,
                            wrong=sr.wrong,
                            blank=sr.blank
                        ))

        return TrendsAnalytics(
            score_trends=score_trends,
            comparisons=comparisons,
            subject_trends=subject_trends
        )

    def _calculate_overall_stats(self, exams: List[Exam]) -> OverviewStats:
        """Calculate overall statistics"""

        total_exams = len(exams)
        net_scores = []
        total_questions = 0
        total_correct = 0

        for exam in exams:
            if exam.exam_result:
                # Convert Decimal to float
                net_scores.append(float(exam.exam_result.net_score))
                total_questions += exam.exam_result.total_questions
                total_correct += exam.exam_result.total_correct

        latest_net = net_scores[0] if net_scores else None
        avg_net = sum(net_scores) / len(net_scores) if net_scores else None
        best_net = max(net_scores) if net_scores else None
        worst_net = min(net_scores) if net_scores else None
        accuracy = (total_correct / total_questions * 100) if total_questions > 0 else None

        return OverviewStats(
            total_exams=total_exams,
            latest_net_score=latest_net,
            average_net_score=avg_net,
            best_score=best_net,
            worst_score=worst_net,
            total_questions_answered=total_questions,
            overall_accuracy=accuracy
        )

    def _get_score_trends(self, exams: List[Exam]) -> List[ScoreTrend]:
        """Get score trends over time"""

        trends = []
        for exam in exams:
            if exam.exam_result:
                trends.append(ScoreTrend(
                    exam_id=exam.id,
                    exam_name=exam.exam_name,
                    exam_date=exam.exam_date,
                    net_score=float(exam.exam_result.net_score),
                    net_percentage=float(exam.exam_result.net_percentage),
                    class_rank=exam.exam_result.class_rank,
                    school_rank=exam.exam_result.school_rank
                ))

        return trends

    def _get_all_subject_performance(self, exams: List[Exam]) -> List[SubjectPerformance]:
        """Get performance for all subjects"""

        # Group by subject
        subject_data = {}

        for exam in exams:
            for sr in exam.subject_results:
                if sr.subject_name not in subject_data:
                    subject_data[sr.subject_name] = []
                subject_data[sr.subject_name].append(sr)

        # Calculate performance for each subject
        performances = []
        for subject_name, results in subject_data.items():
            performance = self._calculate_subject_performance_from_results(subject_name, results)
            performances.append(performance)

        return performances

    def _calculate_subject_performance(
        self,
        subject_name: str,
        subject_results: List[tuple]
    ) -> SubjectPerformance:
        """Calculate subject performance from exam-subject pairs"""

        results = [sr for _, sr in subject_results]
        return self._calculate_subject_performance_from_results(subject_name, results)

    def _calculate_subject_performance_from_results(
        self,
        subject_name: str,
        results: List
    ) -> SubjectPerformance:
        """Calculate performance metrics"""

        total_exams = len(results)
        # Convert Decimal to float for calculations
        nets = [float(r.net_score) for r in results]
        percentages = [float(r.net_percentage) for r in results]

        avg_net = sum(nets) / len(nets) if nets else 0
        avg_percentage = sum(percentages) / len(percentages) if percentages else 0
        best_net = max(nets) if nets else 0
        worst_net = min(nets) if nets else 0

        total_questions = sum(r.total_questions for r in results)
        total_correct = sum(r.correct for r in results)
        total_wrong = sum(r.wrong for r in results)
        total_blank = sum(r.blank for r in results)

        # Simple trend detection
        trend = "stable"
        if len(nets) >= 3:
            recent_avg = sum(nets[:3]) / 3
            older_avg = sum(nets[-3:]) / 3
            if recent_avg > older_avg * 1.1:
                trend = "improving"
            elif recent_avg < older_avg * 0.9:
                trend = "declining"

        return SubjectPerformance(
            subject_name=subject_name,
            total_exams=total_exams,
            average_net=avg_net,
            average_percentage=avg_percentage,
            best_net=best_net,
            worst_net=worst_net,
            total_questions=total_questions,
            total_correct=total_correct,
            total_wrong=total_wrong,
            total_blank=total_blank,
            improvement_trend=trend
        )

    def _get_subject_trends(self, subject_results: List[tuple]) -> List[SubjectTrend]:
        """Get subject trends over time"""

        trends = []
        for exam, sr in subject_results:
            trends.append(SubjectTrend(
                exam_id=exam.id,
                exam_name=exam.exam_name,
                exam_date=exam.exam_date,
                subject_name=sr.subject_name,
                net_score=float(sr.net_score),
                net_percentage=float(sr.net_percentage),
                correct=sr.correct,
                wrong=sr.wrong,
                blank=sr.blank
            ))

        return trends

    def _get_comparisons(self, exams: List[Exam]) -> List[ComparisonData]:
        """Get comparisons with averages"""

        comparisons = []
        for exam in exams:
            if exam.exam_result:
                er = exam.exam_result
                net_score = float(er.net_score)
                class_avg = float(er.class_avg) if er.class_avg else None
                school_avg = float(er.school_avg) if er.school_avg else None
                vs_class = net_score - class_avg if class_avg else None
                vs_school = net_score - school_avg if school_avg else None

                comparisons.append(ComparisonData(
                    exam_id=exam.id,
                    exam_name=exam.exam_name,
                    exam_date=exam.exam_date,
                    student_net=net_score,
                    class_avg=class_avg,
                    school_avg=school_avg,
                    vs_class_diff=vs_class,
                    vs_school_diff=vs_school
                ))

        return comparisons

    def _get_learning_outcome_stats(
        self,
        exams: List[Exam],
        subject_name: Optional[str] = None
    ) -> List[LearningOutcomeStats]:
        """Get learning outcome statistics"""

        # Group by outcome
        outcome_data = {}

        for exam in exams:
            for lo in exam.learning_outcomes:
                if subject_name and lo.subject_name != subject_name:
                    continue

                key = (lo.subject_name, lo.category, lo.subcategory, lo.outcome_description)

                if key not in outcome_data:
                    outcome_data[key] = []
                outcome_data[key].append(lo)

        # Calculate stats
        stats = []
        for (subj, cat, subcat, desc), outcomes in outcome_data.items():
            total_questions = sum(o.total_questions for o in outcomes)
            total_acquired = sum(o.acquired for o in outcomes)

            avg_success = (total_acquired / total_questions * 100) if total_questions > 0 else 0

            stats.append(LearningOutcomeStats(
                subject_name=subj,
                category=cat,
                subcategory=subcat,
                outcome_description=desc,
                total_appearances=len(outcomes),
                total_questions=total_questions,
                total_acquired=total_acquired,
                average_success_rate=avg_success
            ))

        return stats
