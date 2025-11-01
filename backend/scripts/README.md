# Utility Scripts

This directory contains utility scripts for database maintenance and data management.

## Scripts

### Data Cleanup

- **`cleanup_all_data.py`** - Deletes all data from the database (use with caution!)
  - Usage: `python scripts/cleanup_all_data.py`
  - ⚠️ **WARNING:** This will delete all student data, exams, and analytics

- **`cleanup_recs.py`** - Cleans up recommendation data
  - Usage: `python scripts/cleanup_recs.py`

- **`cleanup_resources.py`** - Cleans up resource-related tables (legacy, may be deprecated)
  - Usage: `python scripts/cleanup_resources.py`

### Data Loading

- **`load_curriculum.py`** - Loads high school curriculum data from JSON file
  - Usage: `python scripts/load_curriculum.py`
  - Source: `lise_mufredati.json`
  - Run this after database initialization or to refresh curriculum data

### Data Export

- **`export_curriculum.py`** - Exports curriculum data to JSON file
  - Usage: `python scripts/export_curriculum.py`
  - Output: `../../temp/curriculum_export.json`
  - Exports hierarchical structure: Subjects → Grades → Units → Topics
  - Includes: subject_id, subject_name, grade_id, grade, unit_id, unit_no, unit_name, topic_id, topic_name

- **`export_learning_outcomes.py`** - Exports learning outcomes data to JSON file
  - Usage: `python scripts/export_learning_outcomes.py`
  - Output: `../../temp/learning_outcomes_export.json`
  - Exports unique learning outcomes (excluding merged ones)
  - Includes: id, subject_name, category, subcategory

### Data Normalization

- **`normalize_subjects_db.py`** - One-time script to normalize subject names in the database
  - Usage: `python scripts/normalize_subjects_db.py`
  - Ensures consistent subject naming across all tables

## Running Scripts

All scripts should be run from the backend directory:

```bash
cd /root/projects/deneme-analiz/backend
source venv/bin/activate
python scripts/<script_name>.py
```

## Notes

- Always backup your database before running cleanup scripts
- Check the script contents before running for the first time
- Some scripts are one-time use (like normalization)
- Cleanup scripts are primarily for development environments
