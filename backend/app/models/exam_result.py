"""
ExamResult model for overall exam performance
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class ExamResult(Base):
    """Overall exam result model"""

    __tablename__ = "exam_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String(36), ForeignKey("exams.id"), nullable=False, unique=True, index=True)

    # Overall statistics
    total_questions = Column(Integer, nullable=False)
    total_correct = Column(Integer, nullable=False)
    total_wrong = Column(Integer, nullable=False)
    total_blank = Column(Integer, nullable=False)

    # Net score
    net_score = Column(Numeric(10, 3), nullable=False)
    net_percentage = Column(Numeric(5, 2), nullable=False)

    # Rankings
    class_rank = Column(Integer)
    class_total = Column(Integer)
    school_rank = Column(Integer)
    school_total = Column(Integer)

    # Averages for comparison
    class_avg = Column(Numeric(10, 3))
    school_avg = Column(Numeric(10, 3))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    exam = relationship("Exam", back_populates="exam_result")

    def __repr__(self):
        return f"<ExamResult(net={self.net_score}, rank={self.class_rank}/{self.class_total})>"
