"""
SubjectResult model for per-subject performance
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class SubjectResult(Base):
    """Subject-specific exam result"""

    __tablename__ = "subject_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String(36), ForeignKey("exams.id"), nullable=False, index=True)

    subject_name = Column(String(50), nullable=False, index=True)  # Matematik, Fizik, etc.

    # Question statistics
    total_questions = Column(Integer, nullable=False)
    correct = Column(Integer, nullable=False)
    wrong = Column(Integer, nullable=False)
    blank = Column(Integer, nullable=False)

    # Net score
    net_score = Column(Numeric(10, 3), nullable=False)
    net_percentage = Column(Numeric(5, 2), nullable=False)

    # Rankings
    class_rank = Column(Integer)
    class_avg = Column(Numeric(10, 3))
    school_rank = Column(Integer)
    school_avg = Column(Numeric(10, 3))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    exam = relationship("Exam", back_populates="subject_results")

    def __repr__(self):
        return f"<SubjectResult(subject='{self.subject_name}', net={self.net_score})>"
