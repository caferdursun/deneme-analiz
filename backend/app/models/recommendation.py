"""
Recommendation model for study suggestions
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Recommendation(Base):
    """Study recommendation model"""

    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False, index=True)

    generated_at = Column(DateTime, default=datetime.utcnow)

    priority = Column(Integer, nullable=False)  # 1=highest, 5=lowest

    subject_name = Column(String(50))
    topic = Column(String(255))

    issue_type = Column(String(50))  # weak_area, blank_pattern, declining_trend, etc.
    description = Column(Text, nullable=False)

    action_items = Column(JSON)  # Array of specific actions
    rationale = Column(Text)  # Why this recommendation

    impact_score = Column(Numeric(5, 2))  # Estimated impact on performance

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation(priority={self.priority}, subject='{self.subject_name}', topic='{self.topic}')>"
