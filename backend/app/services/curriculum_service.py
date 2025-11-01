"""
Curriculum Service for managing high school curriculum data
New hierarchy: Subject (Ders) -> Grade (Sınıf) -> Unit (Ünite) -> Topic (Konu)
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models import CurriculumSubject, CurriculumGrade, CurriculumUnit, CurriculumTopic
from app.schemas.curriculum import (
    CurriculumSubjectResponse,
    CurriculumGradeResponse,
    CurriculumFullResponse,
)


class CurriculumService:
    """Service for querying curriculum data"""

    def __init__(self, db: Session):
        self.db = db

    def get_all_curriculum(self) -> CurriculumFullResponse:
        """
        Get the complete curriculum organized by Subject -> Grade -> Unit -> Topic

        Returns:
            CurriculumFullResponse with all subjects and their grade levels
        """
        # Get all subjects with eager loading (Subject -> Grade -> Unit -> Topic)
        subjects = (
            self.db.query(CurriculumSubject)
            .options(
                joinedload(CurriculumSubject.grades)
                .joinedload(CurriculumGrade.units)
                .joinedload(CurriculumUnit.topics)
            )
            .order_by(CurriculumSubject.order, CurriculumSubject.subject_name)
            .all()
        )

        # Build response
        subject_responses = []
        total_subjects = len(subjects)
        total_units = 0
        total_topics = 0

        for subject in subjects:
            subject_responses.append(CurriculumSubjectResponse.from_orm(subject))
            for grade in subject.grades:
                total_units += len(grade.units)
                for unit in grade.units:
                    total_topics += len(unit.topics)

        return CurriculumFullResponse(
            subjects=subject_responses,
            total_subjects=total_subjects,
            total_units=total_units,
            total_topics=total_topics,
        )

    def get_subject_by_name(self, subject_name: str) -> Optional[CurriculumSubjectResponse]:
        """
        Get a specific subject with all its grades, units, and topics

        Args:
            subject_name: Name of the subject

        Returns:
            CurriculumSubjectResponse or None if not found
        """
        subject = (
            self.db.query(CurriculumSubject)
            .options(
                joinedload(CurriculumSubject.grades)
                .joinedload(CurriculumGrade.units)
                .joinedload(CurriculumUnit.topics)
            )
            .filter(CurriculumSubject.subject_name == subject_name)
            .first()
        )

        if not subject:
            return None

        return CurriculumSubjectResponse.from_orm(subject)

    def search_topics(self, query: str, grade: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for topics by keyword

        Args:
            query: Search query string
            grade: Optional grade filter

        Returns:
            List of matching topics with context (subject, grade, unit)
        """
        # Build query with new hierarchy
        topics_query = (
            self.db.query(
                CurriculumTopic,
                CurriculumUnit,
                CurriculumGrade,
                CurriculumSubject
            )
            .join(CurriculumUnit, CurriculumTopic.unit_id == CurriculumUnit.id)
            .join(CurriculumGrade, CurriculumUnit.grade_id == CurriculumGrade.id)
            .join(CurriculumSubject, CurriculumGrade.subject_id == CurriculumSubject.id)
            .filter(CurriculumTopic.topic_name.contains(query))
        )

        if grade:
            topics_query = topics_query.filter(CurriculumGrade.grade == grade)

        results = topics_query.order_by(
            CurriculumSubject.order,
            CurriculumGrade.grade,
            CurriculumUnit.unit_no,
            CurriculumTopic.order
        ).all()

        # Format results
        formatted_results = []
        for topic, unit, curriculum_grade, subject in results:
            formatted_results.append({
                "subject_name": subject.subject_name,
                "grade": curriculum_grade.grade,
                "unit_no": unit.unit_no,
                "unit_name": unit.unit_name,
                "topic_id": topic.id,
                "topic_name": topic.topic_name,
            })

        return formatted_results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get curriculum statistics

        Returns:
            Dict with counts by subject
        """
        # Count unique subjects
        total_subjects = self.db.query(CurriculumSubject).count()

        # Count subject-grade combinations
        total_grade_subjects = self.db.query(CurriculumGrade).count()

        # Count units and topics
        total_units = self.db.query(CurriculumUnit).count()
        total_topics = self.db.query(CurriculumTopic).count()

        return {
            "total_subjects": total_subjects,
            "total_grade_subjects": total_grade_subjects,
            "total_units": total_units,
            "total_topics": total_topics,
        }
