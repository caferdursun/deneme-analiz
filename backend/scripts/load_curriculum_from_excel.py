"""
Load curriculum data from konu_takip_tablosu.xlsx
Structure: exam_type -> subject -> topic
"""
import pandas as pd
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import re

# Database connection
DATABASE_URL = "sqlite:///./deneme_analiz.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Subject ordering (Türkçe, Matematik, Fizik, Kimya first)
SUBJECT_ORDER = {
    'Türkçe': 1,
    'Matematik': 2,
    'Fizik': 3,
    'Kimya': 4,
    'Geometri': 5,
    'Biyoloji': 6,
    'Coğrafya': 7,
    'Tarih': 8,
    'Edebiyat': 9,
    'Felsefe': 10,
    'Din Kültürü': 11,
    'Psikoloji': 12,
    'Sosyoloji': 13,
}

def extract_grade_info(konu_text):
    """Extract grade information from topic name like '(Sınıf:9)' or '(Sınıf:9,10,11)'"""
    match = re.search(r'\(Sınıf:([0-9,]+)\)', konu_text)
    if match:
        return match.group(1)
    return None

def clean_topic_name(konu_text):
    """Remove grade info from topic name"""
    # Remove (Sınıf:X) pattern
    cleaned = re.sub(r'\s*\(Sınıf:[0-9,]+\)\s*', '', konu_text)
    return cleaned.strip()

def load_curriculum_data():
    """Load curriculum from Excel file"""
    print("📂 Loading Excel file...")
    file_path = '/root/projects/deneme-analiz/konu_takip_tablosu.xlsx'
    df = pd.read_excel(file_path)

    print(f"✅ Loaded {len(df)} records")
    print(f"📊 Columns: {list(df.columns)}")

    # Create exam types
    print("\n🎯 Creating exam types...")
    exam_types = {}

    for idx, exam_type_name in enumerate(['TYT', 'AYT'], 1):
        exam_type_id = str(uuid.uuid4())
        session.execute(text("""
            INSERT INTO exam_types (id, name, display_name, "order", created_at)
            VALUES (:id, :name, :display_name, :order, :created_at)
        """), {
            'id': exam_type_id,
            'name': exam_type_name,
            'display_name': 'Temel Yeterlilik Testi' if exam_type_name == 'TYT' else 'Alan Yeterlilik Testi',
            'order': idx,
            'created_at': datetime.utcnow()
        })
        exam_types[exam_type_name] = exam_type_id
        print(f"  ✓ {exam_type_name} ({exam_types[exam_type_name][:8]}...)")

    session.commit()

    # Group data by exam_type and subject
    print("\n📚 Creating subjects and topics...")
    subject_ids = {}

    for exam_type in ['TYT', 'AYT']:
        exam_data = df[df['sinav_türü'] == exam_type]
        subjects_in_exam = exam_data['ders'].unique()

        print(f"\n  {exam_type} ({len(subjects_in_exam)} subjects):")

        for subject_name in subjects_in_exam:
            # Create subject
            subject_key = f"{exam_type}_{subject_name}"
            if subject_key not in subject_ids:
                subject_id = str(uuid.uuid4())
                order = SUBJECT_ORDER.get(subject_name, 99)

                session.execute(text("""
                    INSERT INTO subjects (id, exam_type_id, name, "order", created_at)
                    VALUES (:id, :exam_type_id, :name, :order, :created_at)
                """), {
                    'id': subject_id,
                    'exam_type_id': exam_types[exam_type],
                    'name': subject_name,
                    'order': order,
                    'created_at': datetime.utcnow()
                })
                subject_ids[subject_key] = subject_id

                # Get topics for this subject
                topics = exam_data[exam_data['ders'] == subject_name]['konu'].tolist()
                print(f"    • {subject_name:15s} ({len(topics)} topics)")

                # Insert topics
                for topic_idx, topic_text in enumerate(topics, 1):
                    grade_info = extract_grade_info(topic_text)
                    topic_name = clean_topic_name(topic_text)

                    topic_id = str(uuid.uuid4())
                    session.execute(text("""
                        INSERT INTO topics (id, subject_id, name, grade_info, "order", created_at)
                        VALUES (:id, :subject_id, :name, :grade_info, :order, :created_at)
                    """), {
                        'id': topic_id,
                        'subject_id': subject_id,
                        'name': topic_name,
                        'grade_info': grade_info,
                        'order': topic_idx,
                        'created_at': datetime.utcnow()
                    })

    session.commit()

    # Print statistics
    print("\n" + "=" * 60)
    print("✅ CURRICULUM DATA LOADED SUCCESSFULLY!")
    print("=" * 60)

    # Count records
    exam_types_count = session.execute(text("SELECT COUNT(*) FROM exam_types")).scalar()
    subjects_count = session.execute(text("SELECT COUNT(*) FROM subjects")).scalar()
    topics_count = session.execute(text("SELECT COUNT(*) FROM topics")).scalar()

    print(f"\n📊 Statistics:")
    print(f"  • Exam Types: {exam_types_count}")
    print(f"  • Subjects: {subjects_count}")
    print(f"  • Topics: {topics_count}")

    # Show breakdown
    print(f"\n📋 Breakdown by Exam Type:")
    result = session.execute(text("""
        SELECT et.name, et.display_name, COUNT(DISTINCT s.id) as subject_count, COUNT(t.id) as topic_count
        FROM exam_types et
        LEFT JOIN subjects s ON et.id = s.exam_type_id
        LEFT JOIN topics t ON s.id = t.subject_id
        GROUP BY et.id, et.name, et.display_name
        ORDER BY et."order"
    """))

    for row in result:
        print(f"  • {row.name:3s} - {row.display_name:30s}: {row.subject_count:2d} subjects, {row.topic_count:3d} topics")

    session.close()

if __name__ == "__main__":
    try:
        load_curriculum_data()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        session.rollback()
        session.close()
        raise
