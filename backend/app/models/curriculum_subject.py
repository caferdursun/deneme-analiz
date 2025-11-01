"""
Curriculum Subject model - Top level (Ders)
"""
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class CurriculumSubject(Base):
    """
    Curriculum subject model - Top level (Ders)
    Examples: Matematik, Fizik, Kimya, Biyoloji, etc.
    """

    __tablename__ = "curriculum_subjects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_name = Column(String(100), nullable=False, unique=True, index=True)  # "Matematik", "Fizik", etc.
    order = Column(Integer, default=99)  # For custom ordering (lower = higher priority)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships - one subject has many grade levels
    grades = relationship("CurriculumGrade", back_populates="subject", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CurriculumSubject(subject='{self.subject_name}')>"
