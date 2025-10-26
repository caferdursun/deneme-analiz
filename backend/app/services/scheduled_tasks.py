"""
Scheduled background tasks
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pathlib import Path
import logging

from app.models.exam import Exam
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


def cleanup_unconfirmed_exams():
    """
    Delete exams that have been pending confirmation for more than 24 hours
    """
    db = SessionLocal()
    try:
        # Calculate cutoff time (24 hours ago)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)

        # Find unconfirmed exams older than 24 hours
        old_pending_exams = db.query(Exam).filter(
            Exam.status == "pending_confirmation",
            Exam.uploaded_at < cutoff_time
        ).all()

        if not old_pending_exams:
            logger.info("No unconfirmed exams to cleanup")
            return

        logger.info(f"Found {len(old_pending_exams)} unconfirmed exams to cleanup")

        for exam in old_pending_exams:
            try:
                # Delete PDF file if exists
                if exam.pdf_path and Path(exam.pdf_path).exists():
                    Path(exam.pdf_path).unlink()
                    logger.info(f"Deleted PDF file: {exam.pdf_path}")

                # Delete exam record
                db.delete(exam)
                logger.info(f"Deleted unconfirmed exam: {exam.id} - {exam.exam_name}")
            except Exception as e:
                logger.error(f"Error deleting exam {exam.id}: {str(e)}")
                continue

        # Commit all deletions
        db.commit()
        logger.info(f"Successfully cleaned up {len(old_pending_exams)} unconfirmed exams")

    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        db.rollback()
    finally:
        db.close()


def send_pending_review_reminders():
    """
    Log reminder for exams pending review (future: could send email/notification)
    """
    db = SessionLocal()
    try:
        # Find all pending exams
        pending_exams = db.query(Exam).filter(
            Exam.status == "pending_confirmation"
        ).all()

        if pending_exams:
            logger.info(f"Reminder: {len(pending_exams)} exams pending review")
            for exam in pending_exams:
                hours_pending = (datetime.utcnow() - exam.uploaded_at).total_seconds() / 3600
                logger.info(f"  - {exam.exam_name} (pending for {hours_pending:.1f} hours)")

    except Exception as e:
        logger.error(f"Error checking pending exams: {str(e)}")
    finally:
        db.close()
