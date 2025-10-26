"""
LearningOutcome model for topic-level performance (Kazanım Analizi)
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class LearningOutcome(Base):
    """Learning outcome (kazanım) analysis for specific topics"""

    __tablename__ = "learning_outcomes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String(36), ForeignKey("exams.id"), nullable=False, index=True)

    subject_name = Column(String(50), nullable=False, index=True)

    # Hierarchical topic structure
    category = Column(String(255))  # Main category (e.g., "SAYILAR VE CEBİR")
    subcategory = Column(String(255))  # Subcategory (e.g., "Denklemler ve Eşitsizlikler")
    outcome_description = Column(Text)  # Specific learning outcome

    # Performance metrics
    total_questions = Column(Integer, nullable=False)
    acquired = Column(Integer, nullable=False)  # Kazanılan
    lost = Column(Integer, nullable=False)  # Kaybedilen

    # Success rates
    success_rate = Column(Numeric(5, 2))  # Student's success percentage
    student_percentage = Column(Numeric(5, 2))
    class_percentage = Column(Numeric(5, 2))
    school_percentage = Column(Numeric(5, 2))

    # Merge tracking (soft delete)
    merged_into_id = Column(String(36), ForeignKey("learning_outcomes.id"), nullable=True, index=True)
    is_merged = Column(Integer, default=0)  # 0 = active, 1 = merged into another outcome

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    exam = relationship("Exam", back_populates="learning_outcomes")

    def __repr__(self):
        return f"<LearningOutcome(subject='{self.subject_name}', category='{self.category}', success={self.success_rate}%)>"
