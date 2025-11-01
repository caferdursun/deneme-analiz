"""
Script to load curriculum data from lise_mufredati.json into database
New hierarchy: Ders -> Sınıf -> Ünite -> Konu
"""
import json
import sys
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import SessionLocal
from app.models import CurriculumSubject, CurriculumGrade, CurriculumUnit, CurriculumTopic


# Subject priority order (lower number = higher priority)
SUBJECT_PRIORITY = {
    'Türkçe': 1,
    'Türk Dili ve Edebiyatı': 1,
    'Matematik': 2,
    'Fizik': 3,
    'Kimya': 4,
    'Biyoloji': 5,
    'Geometri': 6,
    'Tarih': 10,
    'Coğrafya': 11,
}


def load_curriculum():
    """Load curriculum data from JSON file with new hierarchy: Ders -> Sınıf -> Ünite -> Konu"""
    db = SessionLocal()

    try:
        # Read JSON file
        with open('lise_mufredati.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"Loading curriculum for {data['egitim_yili']}...")
        print("New hierarchy: Ders -> Sınıf -> Ünite -> Konu\n")

        # Track counts
        total_subjects = 0
        total_grades = 0
        total_units = 0
        total_topics = 0

        # First, collect all unique subjects across all grades
        subjects_dict = {}  # subject_name -> subject_id mapping

        # Scan all grades to find unique subjects
        for sinif_data in data['siniflar']:
            for ders_data in sinif_data['dersler']:
                subject_name = ders_data['ders_adi']
                if subject_name not in subjects_dict:
                    # Get priority order for subject
                    order = SUBJECT_PRIORITY.get(subject_name, 99)

                    # Create subject (top level: Ders)
                    subject = CurriculumSubject(
                        subject_name=subject_name,
                        order=order,
                        created_at=datetime.utcnow()
                    )
                    db.add(subject)
                    db.flush()  # Get subject.id
                    subjects_dict[subject_name] = subject.id
                    total_subjects += 1
                    print(f"✓ Created subject: {subject_name} (order={order})")

        print(f"\n{total_subjects} unique subjects created\n")

        # Now process each grade
        for sinif_data in data['siniflar']:
            grade = sinif_data['sinif']
            print(f"Processing Grade {grade}...")

            # Process each subject in this grade
            for ders_data in sinif_data['dersler']:
                subject_name = ders_data['ders_adi']
                subject_id = subjects_dict[subject_name]

                # Create grade level for this subject (second level: Sınıf)
                curriculum_grade = CurriculumGrade(
                    subject_id=subject_id,
                    grade=grade,
                    created_at=datetime.utcnow()
                )
                db.add(curriculum_grade)
                db.flush()  # Get curriculum_grade.id
                total_grades += 1

                # Process each unit (third level: Ünite)
                for unite_data in ders_data['uniteler']:
                    unit = CurriculumUnit(
                        grade_id=curriculum_grade.id,
                        unit_no=unite_data['unite_no'],
                        unit_name=unite_data['unite_adi'],
                        created_at=datetime.utcnow()
                    )
                    db.add(unit)
                    db.flush()  # Get unit.id
                    total_units += 1

                    # Process each topic (fourth level: Konu)
                    for idx, konu in enumerate(unite_data['konular'], start=1):
                        topic = CurriculumTopic(
                            unit_id=unit.id,
                            topic_name=konu,
                            order=idx,
                            created_at=datetime.utcnow()
                        )
                        db.add(topic)
                        total_topics += 1

                print(f"  ✓ {subject_name}: {len(ders_data['uniteler'])} units, {sum(len(u['konular']) for u in ders_data['uniteler'])} topics")

        # Commit all changes
        db.commit()

        print(f"\n{'='*60}")
        print(f"✅ Successfully loaded curriculum!")
        print(f"{'='*60}")
        print(f"   Unique Subjects: {total_subjects}")
        print(f"   Subject-Grade Combinations: {total_grades}")
        print(f"   Total Units: {total_units}")
        print(f"   Total Topics: {total_topics}")
        print(f"{'='*60}")

    except FileNotFoundError:
        print("❌ Error: lise_mufredati.json not found!")
        print("   Make sure to run this script from the backend directory.")
        sys.exit(1)
    except Exception as e:
        db.rollback()
        print(f"❌ Error loading curriculum: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Curriculum Data Loader")
    print("=" * 60)
    load_curriculum()
