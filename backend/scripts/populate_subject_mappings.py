#!/usr/bin/env python3
"""
Populate Subject Name Mappings Table

This script creates mappings from learning outcome subject names to curriculum subject names.
Each mapping includes the exam type (TYT or AYT) to help with grade and subject filtering during matching.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.models.exam_type import ExamType
from app.models.subject import Subject


def get_exam_type_ids(db: Session) -> dict:
    """Get exam type IDs"""
    exam_types = db.query(ExamType).all()
    return {et.name: et.id for et in exam_types}


def get_subject_name_to_exam_type_id(db: Session) -> dict:
    """Get mapping of curriculum subject name to exam type ID"""
    subjects = db.query(Subject).join(ExamType).all()

    # Group by subject name and collect exam type IDs
    result = {}
    for subject in subjects:
        if subject.name not in result:
            result[subject.name] = []
        result[subject.name].append(subject.exam_type_id)

    return result


def populate_mappings(db: Session):
    """Populate subject name mappings"""

    print("Fetching exam types and subjects...")
    exam_type_ids = get_exam_type_ids(db)
    subject_to_exam_types = get_subject_name_to_exam_type_id(db)

    print(f"Found {len(exam_type_ids)} exam types")
    print(f"Found {len(subject_to_exam_types)} unique curriculum subjects")

    # Define mappings from learning outcome subjects to curriculum subjects
    # Key: outcome subject name -> Value: curriculum subject name
    subject_mappings = {
        # Matematik variations
        "Matematik.09": "Matematik",
        "Matematik.10": "Matematik",
        "Matematik.11": "Matematik",
        "Matematik.12": "Matematik",
        "KURS 11-12. SINIF MATEMATİK": "Matematik",

        # Fizik
        "Fizik.10": "Fizik",
        "Fizik.11": "Fizik",

        # Kimya
        "Kimya.09": "Kimya",
        "Kimya.10": "Kimya",
        "Kimya.11": "Kimya",
        "Kimya.12": "Kimya",

        # Biyoloji
        "Biyoloji.09": "Biyoloji",
        "Biyoloji.10": "Biyoloji",
        "Biyoloji.12": "Biyoloji",

        # Coğrafya
        "Coğrafya.09": "Coğrafya",

        # Tarih
        "Tarih.09": "Tarih",

        # Felsefe
        "Felsefe.10": "Felsefe",

        # Din Kültürü
        "Din Kültürü.09": "Din Kültürü",

        # Edebiyat - Only AYT has Edebiyat
        "12. SINIF KURS EDEBİYAT YKS": "Edebiyat",
    }

    print(f"\nCreating {len(subject_mappings)} subject mappings...")

    created_count = 0
    for outcome_subject, curriculum_subject in subject_mappings.items():
        # Get exam type IDs for this curriculum subject
        if curriculum_subject not in subject_to_exam_types:
            print(f"WARNING: Curriculum subject '{curriculum_subject}' not found in database")
            continue

        exam_type_ids_for_subject = subject_to_exam_types[curriculum_subject]

        # Create mapping for each exam type where this subject appears
        for exam_type_id in exam_type_ids_for_subject:
            # Check if mapping already exists
            existing = db.execute(
                text("""
                SELECT id FROM subject_name_mappings
                WHERE outcome_subject_name = :outcome
                AND curriculum_subject_name = :curriculum
                AND exam_type_id = :exam_type
                """),
                {
                    "outcome": outcome_subject,
                    "curriculum": curriculum_subject,
                    "exam_type": exam_type_id
                }
            ).fetchone()

            if existing:
                continue

            # Insert mapping
            mapping_id = str(uuid.uuid4())
            now = datetime.now()

            db.execute(
                text("""
                INSERT INTO subject_name_mappings
                (id, outcome_subject_name, curriculum_subject_name, exam_type_id, created_at, updated_at)
                VALUES (:id, :outcome, :curriculum, :exam_type, :created_at, :updated_at)
                """),
                {
                    "id": mapping_id,
                    "outcome": outcome_subject,
                    "curriculum": curriculum_subject,
                    "exam_type": exam_type_id,
                    "created_at": now,
                    "updated_at": now
                }
            )
            created_count += 1

    db.commit()
    print(f"\n✓ Created {created_count} subject mappings")

    # Show summary
    print("\n=== Summary ===")
    result = db.execute(text("SELECT COUNT(*) as count FROM subject_name_mappings")).fetchone()
    print(f"Total mappings in database: {result[0]}")

    # Show mappings by exam type
    print("\nMappings by exam type:")
    results = db.execute(text("""
        SELECT e.name, COUNT(*) as count
        FROM subject_name_mappings m
        JOIN exam_types e ON m.exam_type_id = e.id
        GROUP BY e.name
        ORDER BY e.'order'
    """)).fetchall()

    for row in results:
        print(f"  {row[0]}: {row[1]} mappings")


def main():
    """Main entry point"""
    print("Subject Name Mappings Population Script")
    print("=" * 50)

    db = SessionLocal()
    try:
        populate_mappings(db)
        print("\n✓ Script completed successfully!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
