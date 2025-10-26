"""
Exam service for business logic
"""
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid

from app.models import (
    Student,
    Exam,
    ExamResult,
    SubjectResult,
    LearningOutcome,
    Question,
)
from app.utils.claude_client import ClaudeClient
from app.utils.local_pdf_parser import LocalPDFParser
from app.services.validation_service import ValidationService
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ExamService:
    """Service for exam-related operations"""

    def __init__(self, db: Session):
        self.db = db
        self.claude_client = None

    def _get_claude_client(self) -> ClaudeClient:
        """Lazy initialization of Claude client"""
        if self.claude_client is None:
            self.claude_client = ClaudeClient()
        return self.claude_client

    def get_or_create_student(self, student_data: Dict[str, Any]) -> Student:
        """Get existing student or create new one"""
        # Check if student exists by name and school
        student = (
            self.db.query(Student)
            .filter(
                Student.name == student_data["name"],
                Student.school == student_data["school"],
            )
            .first()
        )

        if not student:
            student = Student(
                name=student_data["name"],
                school=student_data["school"],
                grade=student_data.get("grade"),
                class_section=student_data.get("class_section"),
                program="MF",  # Default to Math-Science
            )
            self.db.add(student)
            self.db.commit()
            self.db.refresh(student)

        return student

    def save_pdf_file(self, pdf_file, filename: str) -> str:
        """Save uploaded PDF file to storage"""
        # Create data directory if it doesn't exist
        storage_path = Path(settings.PDF_STORAGE_PATH)
        storage_path.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix
        unique_filename = f"{file_id}{file_extension}"
        file_path = storage_path / unique_filename

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(pdf_file, buffer)

        return str(file_path)

    def process_exam_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process exam PDF and store temporary data for validation review

        Returns:
            Dictionary with exam_id and validation_report
        """
        import json

        # Parse PDF locally for validation
        logger.info(f"Starting local PDF parsing: {pdf_path}")
        local_parser = LocalPDFParser()
        local_data = local_parser.parse_pdf(pdf_path)
        logger.info(f"Local parsing completed")

        # Analyze PDF with Claude
        logger.info(f"Starting Claude AI analysis: {pdf_path}")
        claude = self._get_claude_client()
        extracted_data = claude.analyze_exam_pdf(pdf_path)
        logger.info(f"Claude analysis completed")

        # Validate Claude output against local parsing
        logger.info(f"Starting validation")
        validator = ValidationService(tolerance=0.1)
        validation_report = validator.validate(extracted_data, local_data)
        logger.info(f"Validation completed: {validation_report['status']}")

        # Log validation issues
        if validation_report['errors'] > 0:
            logger.error(f"Validation errors found: {validation_report['errors']}")
            for issue in validation_report['issues']:
                if issue['severity'] == 'error':
                    logger.error(f"  {issue['field']}: Claude={issue['claude_value']}, Local={issue['local_value']}")
        elif validation_report['warnings'] > 0:
            logger.warning(f"Validation warnings found: {validation_report['warnings']}")

        # Get or create student
        student = self.get_or_create_student(extracted_data["student"])

        # Create exam record with temporary data for review
        exam_data = extracted_data["exam"]
        exam_date_str = exam_data["exam_date"]
        if isinstance(exam_date_str, str):
            exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
        else:
            exam_date = exam_date_str

        exam = Exam(
            student_id=student.id,
            exam_name=exam_data["exam_name"],
            exam_date=exam_date,
            booklet_type=exam_data.get("booklet_type"),
            exam_number=exam_data.get("exam_number"),
            pdf_path=pdf_path,
            processed_at=datetime.utcnow(),
            # Store temporary data for validation review
            status="pending_confirmation",
            claude_data=json.dumps(extracted_data, ensure_ascii=False, indent=2),
            local_data=json.dumps(local_data, ensure_ascii=False, indent=2),
            validation_report=json.dumps(validation_report, ensure_ascii=False, indent=2),
        )
        self.db.add(exam)

        # Commit only the exam record (no related data yet)
        self.db.commit()
        self.db.refresh(exam)

        logger.info(f"Exam created with pending_confirmation status: {exam.id}")

        return {
            "exam_id": exam.id,
            "validation_report": validation_report,
        }

    def get_all_exams(self, student_id: Optional[str] = None) -> List[Exam]:
        """Get all exams, optionally filtered by student"""
        query = self.db.query(Exam)
        if student_id:
            query = query.filter(Exam.student_id == student_id)
        return query.order_by(Exam.exam_date.desc()).all()

    def get_exam_by_id(self, exam_id: str) -> Optional[Exam]:
        """Get exam by ID with all related data"""
        return self.db.query(Exam).filter(Exam.id == exam_id).first()

    def get_exam_details(self, exam_id: str) -> Optional[Dict[str, Any]]:
        """Get complete exam details including all results"""
        exam = self.get_exam_by_id(exam_id)
        if not exam:
            return None

        return {
            "exam": exam,
            "student": exam.student,
            "overall_result": exam.exam_result,
            "subject_results": exam.subject_results,
            "learning_outcomes": exam.learning_outcomes,
            "questions": exam.questions,
        }

    def delete_exam(self, exam_id: str) -> bool:
        """Delete exam and all related data"""
        exam = self.get_exam_by_id(exam_id)
        if not exam:
            return False

        # Delete PDF file if exists
        if exam.pdf_path and Path(exam.pdf_path).exists():
            Path(exam.pdf_path).unlink()

        # Delete exam (cascade will delete related records)
        self.db.delete(exam)
        self.db.commit()

        return True
