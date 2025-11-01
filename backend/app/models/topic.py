"""
Topic Model - Represents topics within subjects
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Topic(Base):
    """Topic model for curriculum hierarchy"""
    __tablename__ = "topics"

    id = Column(String(36), primary_key=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(500), nullable=False)
    grade_info = Column(String(50), nullable=True)  # e.g., "9", "9,10", "9,10,11"
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

    # Relationships
    subject = relationship("Subject", back_populates="topics")
