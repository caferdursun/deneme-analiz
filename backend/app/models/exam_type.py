"""
ExamType Model - Represents exam types (TYT, AYT)
"""
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class ExamType(Base):
    """ExamType model for curriculum hierarchy"""
    __tablename__ = "exam_types"

    id = Column(String(36), primary_key=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    display_name = Column(String(100), nullable=False)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

    # Relationships
    subjects = relationship("Subject", back_populates="exam_type", cascade="all, delete-orphan")
