"""
Question model for individual question tracking
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Question(Base):
    """Individual question tracking"""

    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String(36), ForeignKey("exams.id"), nullable=False, index=True)

    subject_name = Column(String(50), nullable=False, index=True)
    question_number = Column(Integer, nullable=False)

    correct_answer = Column(String(1))  # A, B, C, D, E
    student_answer = Column(String(1))  # A, B, C, D, E, or None

    is_correct = Column(Boolean, default=False)
    is_blank = Column(Boolean, default=False)
    is_canceled = Column(Boolean, default=False)  # İptal edilen sorular

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    exam = relationship("Exam", back_populates="questions")

    def __repr__(self):
        return f"<Question(subject='{self.subject_name}', q={self.question_number}, correct={self.is_correct})>"
