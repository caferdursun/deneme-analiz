"""
Study Plan Item model for individual study tasks
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class StudyPlanItem(Base):
    """Individual study task within a day's schedule"""

    __tablename__ = "study_plan_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    day_id = Column(String(36), ForeignKey("study_plan_days.id"), nullable=False, index=True)
    recommendation_id = Column(String(36), ForeignKey("recommendations.id"), nullable=True)  # Optional link to recommendation

    subject_name = Column(String(50), nullable=False)  # e.g., "Matematik"
    topic = Column(String(255), nullable=False)  # e.g., "Permütasyon ve Kombinasyon"
    description = Column(Text)  # Detailed description of what to study

    duration_minutes = Column(Integer, nullable=False)  # Duration for this specific item
    order = Column(Integer, nullable=False)  # Order within the day (1, 2, 3, ...)

    completed = Column(Boolean, default=False, index=True)
    completed_at = Column(DateTime)  # When this item was marked complete

    # Relationships
    day = relationship("StudyPlanDay", back_populates="items")
    recommendation = relationship("Recommendation")

    def __repr__(self):
        return f"<StudyPlanItem(subject='{self.subject_name}', topic='{self.topic}', duration={self.duration_minutes}, completed={self.completed})>"
