"""
Export learning outcomes data to JSON
"""
import json
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "sqlite:///./deneme_analiz.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Query to get learning outcomes data (only active, non-merged records)
query = """
SELECT DISTINCT
    id,
    subject_name,
    category,
    subcategory
FROM learning_outcomes
WHERE is_merged = 0
ORDER BY subject_name, category, subcategory
"""

# Execute query
result = session.execute(text(query))

# Build list structure
learning_outcomes = []

for row in result:
    learning_outcomes.append({
        'id': row.id,
        'subject_name': row.subject_name,
        'category': row.category,
        'subcategory': row.subcategory
    })

# Write to JSON file
output_path = os.path.join(os.path.dirname(__file__), '../../temp/learning_outcomes_export.json')
output_path = os.path.abspath(output_path)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(learning_outcomes, f, ensure_ascii=False, indent=2)

print(f"✅ Learning outcomes exported to {output_path}")
print(f"📊 Stats:")
print(f"  - Total learning outcomes: {len(learning_outcomes)}")

# Count by subject
subjects = {}
for lo in learning_outcomes:
    subject = lo['subject_name']
    subjects[subject] = subjects.get(subject, 0) + 1

print(f"  - Subjects breakdown:")
for subject, count in sorted(subjects.items()):
    print(f"    • {subject}: {count}")

session.close()
