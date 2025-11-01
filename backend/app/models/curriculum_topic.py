"""
Curriculum Topic model
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class CurriculumTopic(Base):
    """Curriculum topic model for storing topics within units"""

    __tablename__ = "curriculum_topics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    unit_id = Column(String(36), ForeignKey("curriculum_units.id"), nullable=False, index=True)
    topic_name = Column(String(500), nullable=False)  # Topic/konu text
    order = Column(Integer, nullable=False)  # Order within the unit

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    unit = relationship("CurriculumUnit", back_populates="topics")

    def __repr__(self):
        return f"<CurriculumTopic(name='{self.topic_name[:50]}')>"
