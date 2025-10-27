"""
Study Plan model for personalized study schedules
"""
from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class StudyPlan(Base):
    """Study plan model for generating personalized study schedules"""

    __tablename__ = "study_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)  # e.g., "2 Haftalık Matematik Yoğunlaşma Planı"

    time_frame = Column(Integer, nullable=False)  # Duration in days: 7, 14, 30
    daily_study_time = Column(Integer, nullable=False)  # Minutes per day
    study_style = Column(String(20), nullable=False)  # 'intensive', 'balanced', 'relaxed'

    status = Column(String(20), default='active', index=True)  # 'active', 'completed', 'archived'

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    description = Column(Text)  # Optional description/notes

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="study_plans")
    days = relationship("StudyPlanDay", back_populates="plan", cascade="all, delete-orphan", order_by="StudyPlanDay.day_number")

    def __repr__(self):
        return f"<StudyPlan(name='{self.name}', time_frame={self.time_frame}, status='{self.status}')>"
