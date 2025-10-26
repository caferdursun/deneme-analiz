"""
Exam API endpoints
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import tempfile
import shutil

from app.core.database import get_db
from app.services.exam_service import ExamService
from app.schemas.exam import (
    ExamUploadResponse,
    ExamListResponse,
    ExamDetailResponse,
    ExamResponse,
    StudentResponse,
    ExamResultResponse,
    SubjectResultResponse,
    LearningOutcomeResponse,
    QuestionResponse,
)

router = APIRouter()


@router.post("/upload", response_model=ExamUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_exam_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload and process an exam PDF

    - Accepts PDF file
    - Analyzes with Claude AI
    - Stores all exam data
    - Returns exam ID
    """
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted"
        )

    # Create service
    exam_service = ExamService(db)

    try:
        # Save PDF to temporary location first
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name

        # Save to permanent storage
        pdf_path = exam_service.save_pdf_file(open(tmp_path, "rb"), file.filename)

        # Process exam PDF (now returns dict with exam_id and validation_report)
        result = exam_service.process_exam_pdf(pdf_path)

        # Extract validation status
        validation_status = result["validation_report"]["status"]
        validation_summary = result["validation_report"]["summary"]

        # Build response message
        if validation_status == "passed":
            message = "Exam PDF processed successfully. Validation passed."
        elif validation_status == "warning":
            message = f"Exam PDF processed with warnings. {validation_summary}"
        else:
            message = f"Exam PDF processed with errors. {validation_summary}"

        return ExamUploadResponse(
            exam_id=result["exam_id"],
            message=message,
            status="success",
            validation_report=result["validation_report"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid PDF format or data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process exam PDF: {str(e)}"
        )


@router.get("", response_model=ExamListResponse)
async def get_exams(
    student_id: str = None,
    db: Session = Depends(get_db),
):
    """
    Get list of all exams

    - Optionally filter by student_id
    - Returns exams ordered by date (newest first)
    """
    exam_service = ExamService(db)
    exams = exam_service.get_all_exams(student_id=student_id)

    return ExamListResponse(
        exams=[ExamResponse.model_validate(exam) for exam in exams],
        total=len(exams)
    )


@router.get("/{exam_id}", response_model=ExamDetailResponse)
async def get_exam_detail(
    exam_id: str,
    db: Session = Depends(get_db),
):
    """
    Get detailed exam information

    - Returns complete exam data
    - Includes student info
    - Includes all results, learning outcomes, and questions
    """
    exam_service = ExamService(db)
    exam_details = exam_service.get_exam_details(exam_id)

    if not exam_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam with id {exam_id} not found"
        )

    return ExamDetailResponse(
        exam=ExamResponse.model_validate(exam_details["exam"]),
        student=StudentResponse.model_validate(exam_details["student"]),
        overall_result=ExamResultResponse.model_validate(exam_details["overall_result"]) if exam_details["overall_result"] else None,
        subject_results=[SubjectResultResponse.model_validate(sr) for sr in exam_details["subject_results"]],
        learning_outcomes=[LearningOutcomeResponse.model_validate(lo) for lo in exam_details["learning_outcomes"]],
        questions=[QuestionResponse.model_validate(q) for q in exam_details["questions"]]
    )


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    exam_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete an exam

    - Deletes exam and all related data
    - Deletes PDF file from storage
    """
    exam_service = ExamService(db)
    success = exam_service.delete_exam(exam_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam with id {exam_id} not found"
        )

    return None
