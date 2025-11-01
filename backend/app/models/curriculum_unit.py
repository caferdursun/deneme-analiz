"""
Curriculum Unit model - Third level (Ünite)
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class CurriculumUnit(Base):
    """
    Curriculum unit model - Third level (Ünite)
    Represents a unit within a subject-grade combination
    """

    __tablename__ = "curriculum_units"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grade_id = Column(String(36), ForeignKey("curriculum_grades.id"), nullable=False, index=True)
    unit_no = Column(Integer, nullable=False)
    unit_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    grade = relationship("CurriculumGrade", back_populates="units")
    topics = relationship("CurriculumTopic", back_populates="unit", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CurriculumUnit(unit_no={self.unit_no}, name='{self.unit_name}')>"
