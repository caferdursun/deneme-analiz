"""
Subject Model - Represents subjects within exam types
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Subject(Base):
    """Subject model for curriculum hierarchy"""
    __tablename__ = "subjects"

    id = Column(String(36), primary_key=True)
    exam_type_id = Column(String(36), ForeignKey("exam_types.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

    # Relationships
    exam_type = relationship("ExamType", back_populates="subjects")
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")
