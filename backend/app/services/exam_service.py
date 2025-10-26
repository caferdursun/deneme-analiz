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
        Process exam PDF and store all data with validation

        Returns:
            Dictionary with exam_id and validation_report
        """
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

        # Create exam record
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
        )
        self.db.add(exam)
        self.db.flush()  # Get exam.id without committing

        # Create overall exam result
        overall = extracted_data["overall_result"]
        exam_result = ExamResult(
            exam_id=exam.id,
            total_questions=overall["total_questions"],
            total_correct=overall["total_correct"],
            total_wrong=overall["total_wrong"],
            total_blank=overall["total_blank"],
            net_score=overall["net_score"],
            net_percentage=overall["net_percentage"],
            class_rank=overall.get("class_rank"),
            class_total=overall.get("class_total"),
            school_rank=overall.get("school_rank"),
            school_total=overall.get("school_total"),
            class_avg=overall.get("class_avg"),
            school_avg=overall.get("school_avg"),
        )
        self.db.add(exam_result)

        # Create subject results
        for subject_data in extracted_data["subjects"]:
            subject_result = SubjectResult(
                exam_id=exam.id,
                subject_name=subject_data["subject_name"],
                total_questions=subject_data["total_questions"],
                correct=subject_data["correct"],
                wrong=subject_data["wrong"],
                blank=subject_data["blank"],
                net_score=subject_data["net_score"],
                net_percentage=subject_data["net_percentage"],
                class_rank=subject_data.get("class_rank"),
                class_avg=subject_data.get("class_avg"),
                school_rank=subject_data.get("school_rank"),
                school_avg=subject_data.get("school_avg"),
            )
            self.db.add(subject_result)

        # Create learning outcomes
        for outcome_data in extracted_data.get("learning_outcomes", []):
            learning_outcome = LearningOutcome(
                exam_id=exam.id,
                subject_name=outcome_data["subject_name"],
                category=outcome_data.get("category"),
                subcategory=outcome_data.get("subcategory"),
                outcome_description=outcome_data.get("outcome_description"),
                total_questions=outcome_data["total_questions"],
                acquired=outcome_data["acquired"],
                lost=outcome_data["lost"],
                success_rate=outcome_data.get("success_rate"),
                student_percentage=outcome_data.get("student_percentage"),
                class_percentage=outcome_data.get("class_percentage"),
                school_percentage=outcome_data.get("school_percentage"),
            )
            self.db.add(learning_outcome)

        # Create questions
        for question_data in extracted_data.get("questions", []):
            question = Question(
                exam_id=exam.id,
                subject_name=question_data["subject_name"],
                question_number=question_data["question_number"],
                correct_answer=question_data["correct_answer"],
                student_answer=question_data.get("student_answer"),
                is_correct=question_data["is_correct"],
                is_blank=question_data["is_blank"],
            )
            self.db.add(question)

        # Commit all changes
        self.db.commit()
        self.db.refresh(exam)

        return {
            "exam_id": exam.id,
            "validation_report": validation_report,
            "local_data": local_data  # Include for debugging if needed
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
