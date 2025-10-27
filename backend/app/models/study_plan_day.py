"""
Study Plan Day model for daily schedules
"""
from sqlalchemy import Column, String, Integer, Date, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class StudyPlanDay(Base):
    """Daily schedule within a study plan"""

    __tablename__ = "study_plan_days"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String(36), ForeignKey("study_plans.id"), nullable=False, index=True)

    day_number = Column(Integer, nullable=False)  # 1-based day index (1, 2, 3, ...)
    date = Column(Date, nullable=False)  # Actual calendar date

    total_duration_minutes = Column(Integer, default=0)  # Sum of all items' duration
    completed = Column(Boolean, default=False, index=True)  # All items completed?

    notes = Column(Text)  # Optional notes for this day

    # Relationships
    plan = relationship("StudyPlan", back_populates="days")
    items = relationship("StudyPlanItem", back_populates="day", cascade="all, delete-orphan", order_by="StudyPlanItem.order")

    def __repr__(self):
        return f"<StudyPlanDay(day={self.day_number}, date={self.date}, completed={self.completed})>"
