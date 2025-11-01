"""
Curriculum API Routes
Endpoints for accessing curriculum data (ExamType -> Subject -> Topic)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List

from app.core.database import get_db
from app.models.exam_type import ExamType
from app.models.subject import Subject
from app.models.topic import Topic
from app.schemas.curriculum import (
    ExamTypeResponse,
    SubjectResponse,
    TopicResponse,
    CurriculumFullResponse,
    ExamTypeSummary,
    SubjectSummary,
    TopicSummary,
)

router = APIRouter()


@router.get("/curriculum", response_model=CurriculumFullResponse)
async def get_full_curriculum(db: Session = Depends(get_db)):
    """
    Get the full curriculum hierarchy: ExamType -> Subject -> Topic
    """
    # Fetch all exam types with their subjects and topics (eager loading)
    exam_types = (
        db.query(ExamType)
        .options(
            joinedload(ExamType.subjects).joinedload(Subject.topics)
        )
        .order_by(ExamType.order)
        .all()
    )

    # Count totals
    total_exam_types = len(exam_types)
    total_subjects = db.query(Subject).count()
    total_topics = db.query(Topic).count()

    return CurriculumFullResponse(
        exam_types=exam_types,
        total_exam_types=total_exam_types,
        total_subjects=total_subjects,
        total_topics=total_topics,
    )


@router.get("/curriculum/exam-types", response_model=List[ExamTypeResponse])
async def get_exam_types(db: Session = Depends(get_db)):
    """
    Get all exam types with their subjects and topics
    """
    exam_types = (
        db.query(ExamType)
        .options(
            joinedload(ExamType.subjects).joinedload(Subject.topics)
        )
        .order_by(ExamType.order)
        .all()
    )
    return exam_types


@router.get("/curriculum/exam-types/{exam_type_id}", response_model=ExamTypeResponse)
async def get_exam_type(exam_type_id: str, db: Session = Depends(get_db)):
    """
    Get a specific exam type with its subjects and topics
    """
    exam_type = (
        db.query(ExamType)
        .options(
            joinedload(ExamType.subjects).joinedload(Subject.topics)
        )
        .filter(ExamType.id == exam_type_id)
        .first()
    )

    if not exam_type:
        raise HTTPException(status_code=404, detail="Exam type not found")

    return exam_type


@router.get("/curriculum/exam-types/{exam_type_id}/subjects", response_model=List[SubjectResponse])
async def get_subjects_by_exam_type(exam_type_id: str, db: Session = Depends(get_db)):
    """
    Get all subjects for a specific exam type with their topics
    """
    subjects = (
        db.query(Subject)
        .options(joinedload(Subject.topics))
        .filter(Subject.exam_type_id == exam_type_id)
        .order_by(Subject.order)
        .all()
    )
    return subjects


@router.get("/curriculum/subjects/{subject_id}", response_model=SubjectResponse)
async def get_subject(subject_id: str, db: Session = Depends(get_db)):
    """
    Get a specific subject with its topics
    """
    subject = (
        db.query(Subject)
        .options(joinedload(Subject.topics))
        .filter(Subject.id == subject_id)
        .first()
    )

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    return subject


@router.get("/curriculum/subjects/{subject_id}/topics", response_model=List[TopicResponse])
async def get_topics_by_subject(subject_id: str, db: Session = Depends(get_db)):
    """
    Get all topics for a specific subject
    """
    topics = (
        db.query(Topic)
        .filter(Topic.subject_id == subject_id)
        .order_by(Topic.order)
        .all()
    )
    return topics


@router.get("/curriculum/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: str, db: Session = Depends(get_db)):
    """
    Get a specific topic
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    return topic


@router.get("/curriculum/summary", response_model=List[ExamTypeSummary])
async def get_curriculum_summary(db: Session = Depends(get_db)):
    """
    Get a summary of the curriculum with counts
    """
    exam_types = db.query(ExamType).order_by(ExamType.order).all()

    result = []
    for exam_type in exam_types:
        subject_count = db.query(Subject).filter(Subject.exam_type_id == exam_type.id).count()
        topic_count = (
            db.query(Topic)
            .join(Subject)
            .filter(Subject.exam_type_id == exam_type.id)
            .count()
        )

        result.append(
            ExamTypeSummary(
                id=exam_type.id,
                name=exam_type.name,
                display_name=exam_type.display_name,
                subject_count=subject_count,
                topic_count=topic_count,
            )
        )

    return result
