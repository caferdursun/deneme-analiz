"""
Exam API endpoints
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Body
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
    status: str = None,
    db: Session = Depends(get_db),
):
    """
    Get list of all exams

    - Optionally filter by student_id
    - Optionally filter by status (pending_confirmation, confirmed)
    - Returns exams ordered by date (newest first)
    """
    exam_service = ExamService(db)

    # Filter by status if provided
    if status:
        from app.models.exam import Exam
        query = db.query(Exam)
        if student_id:
            query = query.filter(Exam.student_id == student_id)
        query = query.filter(Exam.status == status)
        exams = query.order_by(Exam.exam_date.desc()).all()
    else:
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


@router.get("/stats/pending-count")
async def get_pending_exams_count(
    student_id: str = None,
    db: Session = Depends(get_db),
):
    """
    Get count of pending confirmation exams

    - Optionally filter by student_id
    - Returns count of exams awaiting confirmation
    """
    from app.models.exam import Exam

    query = db.query(Exam).filter(Exam.status == "pending_confirmation")
    if student_id:
        query = query.filter(Exam.student_id == student_id)

    count = query.count()

    return {
        "pending_count": count,
        "student_id": student_id
    }


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


@router.post("/{exam_id}/confirm")
async def confirm_exam(
    exam_id: str,
    data_source: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """
    Confirm exam data and choose data source

    - Accepts data_source: "claude" or "local"
    - Commits chosen data to database
    - Marks exam as confirmed
    """
    from app.models.exam import Exam
    from app.models.exam_result import ExamResult
    from app.models.subject_result import SubjectResult
    from app.models.learning_outcome import LearningOutcome
    from app.models.question import Question
    from datetime import datetime
    import json

    # Get exam directly from DB
    exam = db.query(Exam).filter(Exam.id == exam_id).first()

    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam with id {exam_id} not found"
        )

    if exam.status == "confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam already confirmed"
        )

    # Validate data_source
    if data_source not in ["claude", "local"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="data_source must be 'claude' or 'local'"
        )

    # Parse the chosen data source
    if data_source == "claude":
        if not exam.claude_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Claude data not available"
            )
        chosen_data = json.loads(exam.claude_data)
    else:  # local
        if not exam.local_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Local data not available"
            )
        chosen_data = json.loads(exam.local_data)

    # Create overall exam result
    overall = chosen_data["overall_result"]
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
    db.add(exam_result)

    # Create subject results
    for subject_data in chosen_data["subjects"]:
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
        db.add(subject_result)

    # Create learning outcomes
    for outcome_data in chosen_data.get("learning_outcomes", []):
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
        db.add(learning_outcome)

    # Create questions
    for question_data in chosen_data.get("questions", []):
        question = Question(
            exam_id=exam.id,
            subject_name=question_data["subject_name"],
            question_number=question_data["question_number"],
            correct_answer=question_data["correct_answer"],
            student_answer=question_data.get("student_answer"),
            is_correct=question_data["is_correct"],
            is_blank=question_data["is_blank"],
        )
        db.add(question)

    # Update exam status
    exam.status = "confirmed"
    exam.confirmed_at = datetime.utcnow()

    # Commit all changes
    db.commit()

    return {
        "message": "Exam confirmed successfully",
        "exam_id": exam_id,
        "data_source": data_source,
        "status": exam.status
    }
