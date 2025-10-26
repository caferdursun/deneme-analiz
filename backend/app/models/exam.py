"""
Exam model
"""
from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class ExamStatus(str, enum.Enum):
    """Exam confirmation status"""
    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"


class Exam(Base):
    """Exam model for storing exam metadata"""

    __tablename__ = "exams"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False, index=True)

    exam_name = Column(String(255), nullable=False)
    exam_date = Column(Date, nullable=False, index=True)
    booklet_type = Column(String(10))  # A, B, C, D
    exam_number = Column(Integer)  # Sequential exam number

    pdf_path = Column(String(500))  # Path to original PDF

    # Confirmation status - using String for SQLite compatibility
    status = Column(String(30), default="confirmed", nullable=False)

    # Temporary storage for validation review
    claude_data = Column(Text)  # JSON string of Claude API results
    local_data = Column(Text)  # JSON string of local parser results
    validation_report = Column(Text)  # JSON string of validation report

    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)  # When PDF analysis completed
    confirmed_at = Column(DateTime)  # When user confirmed the data

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="exams")
    exam_result = relationship("ExamResult", back_populates="exam", uselist=False, cascade="all, delete-orphan")
    subject_results = relationship("SubjectResult", back_populates="exam", cascade="all, delete-orphan")
    learning_outcomes = relationship("LearningOutcome", back_populates="exam", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Exam(name='{self.exam_name}', date='{self.exam_date}')>"
