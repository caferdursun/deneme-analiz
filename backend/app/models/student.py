"""
Student model
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Student(Base):
    """Student model for storing student information"""

    __tablename__ = "students"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    school = Column(String(255))
    grade = Column(String(10))  # e.g., "12"
    class_section = Column(String(10))  # e.g., "12/B"
    program = Column(String(10))  # e.g., "MF" (Math-Science), "TM" (Turkish-Math)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exams = relationship("Exam", back_populates="student", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="student", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(name='{self.name}', school='{self.school}', class='{self.class_section}')>"
