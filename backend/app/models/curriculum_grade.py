"""
Curriculum Grade model - Second level (Sınıf)
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class CurriculumGrade(Base):
    """
    Curriculum grade model - Second level (Sınıf)
    Represents a subject at a specific grade level
    Examples: Matematik-9, Fizik-10, etc.
    """

    __tablename__ = "curriculum_grades"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String(36), ForeignKey("curriculum_subjects.id"), nullable=False, index=True)
    grade = Column(String(2), nullable=False, index=True)  # "9", "10", "11", "12"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subject = relationship("CurriculumSubject", back_populates="grades")
    units = relationship("CurriculumUnit", back_populates="grade", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CurriculumGrade(subject_id='{self.subject_id}', grade='{self.grade}')>"
