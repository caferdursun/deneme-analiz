# Database Schema Documentation

## Overview
This document provides a comprehensive overview of the database schema for the **Deneme Analiz** application - a university exam preparation analysis system.

**Database Type:** SQLite
**ORM:** SQLAlchemy
**Migrations:** Alembic
**Current Migration:** ffdbec01cad2 (Restructure curriculum schema)

---

## Current Data Status

| Table | Row Count | Description |
|-------|-----------|-------------|
| students | 1 | Student profiles |
| exams | 8 | Mock exams uploaded |
| exam_results | 8 | Overall exam results |
| subject_results | 55 | Subject-wise results |
| learning_outcomes | 299 | Topic-level performance tracking |
| questions | 702 | Individual question records |
| recommendations | 8 | Study recommendations |
| study_plans | 1 | Active study plans |
| curriculum_subjects | 7 | High school subjects |
| curriculum_grades | 28 | Subject-grade combinations (7×4) |
| curriculum_units | 112 | Curriculum units |
| curriculum_topics | 686 | Individual topics |

---

## Schema Structure

### 1. Student & Identity

#### **students**
Core student information table.

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `name` (VARCHAR(255), NOT NULL, INDEXED) - Student full name
- `school` (VARCHAR(255)) - School name
- `grade` (VARCHAR(10)) - Current grade (e.g., "12")
- `class_section` (VARCHAR(10)) - Class section (e.g., "12/B")
- `program` (VARCHAR(10)) - Academic track (e.g., "MF" for Math-Science)
- `created_at` (DATETIME) - Record creation timestamp
- `updated_at` (DATETIME) - Last update timestamp

**Relationships:**
- `exams` → One-to-Many with `exams`
- `recommendations` → One-to-Many with `recommendations`
- `study_plans` → One-to-Many with `study_plans`

**Indexes:**
- `ix_students_name` on `name`

---

### 2. Exam Data

#### **exams**
Stores exam metadata and processing status.

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `student_id` (FK → students.id, NOT NULL, INDEXED) - References student
- `exam_name` (VARCHAR(255), NOT NULL) - Exam name/title
- `exam_date` (DATE, NOT NULL, INDEXED) - Exam date
- `booklet_type` (VARCHAR(10)) - Booklet variant (A, B, C, D)
- `exam_number` (INTEGER) - Sequential exam number
- `pdf_path` (VARCHAR(500)) - Path to uploaded PDF
- `status` (VARCHAR(25), DEFAULT 'confirmed') - Confirmation status
- `claude_data` (TEXT) - JSON: Claude API extraction results
- `local_data` (TEXT) - JSON: Local parser results
- `validation_report` (TEXT) - JSON: Validation comparison report
- `uploaded_at` (DATETIME) - Upload timestamp
- `processed_at` (DATETIME) - PDF processing completion time
- `confirmed_at` (DATETIME) - User confirmation timestamp
- `created_at` (DATETIME) - Record creation

**Relationships:**
- `student` → Many-to-One with `students`
- `exam_result` → One-to-One with `exam_results`
- `subject_results` → One-to-Many with `subject_results`
- `learning_outcomes` → One-to-Many with `learning_outcomes`
- `questions` → One-to-Many with `questions`

**Indexes:**
- `ix_exams_student_id` on `student_id`
- `ix_exams_exam_date` on `exam_date`

**Cascade:** All child records (results, outcomes, questions) are deleted when exam is deleted.

---

#### **exam_results**
Overall exam performance summary.

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `exam_id` (FK → exams.id, UNIQUE, NOT NULL, INDEXED) - References exam
- `total_questions` (INTEGER, NOT NULL) - Total question count
- `total_correct` (INTEGER, NOT NULL) - Correct answers
- `total_wrong` (INTEGER, NOT NULL) - Wrong answers
- `total_blank` (INTEGER, NOT NULL) - Blank answers
- `net_score` (NUMERIC(10,3), NOT NULL) - Net = Correct - (Wrong/4)
- `net_percentage` (NUMERIC(5,2), NOT NULL) - Net as percentage
- `class_rank` (INTEGER) - Rank within class
- `class_total` (INTEGER) - Total students in class
- `school_rank` (INTEGER) - Rank within school
- `school_total` (INTEGER) - Total students in school
- `class_avg` (NUMERIC(10,3)) - Class average net score
- `school_avg` (NUMERIC(10,3)) - School average net score
- `created_at` (DATETIME) - Record creation

**Relationships:**
- `exam` → One-to-One with `exams`

**Indexes:**
- `ix_exam_results_exam_id` (UNIQUE) on `exam_id`

---

#### **subject_results**
Per-subject detailed performance.

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `exam_id` (FK → exams.id, NOT NULL, INDEXED) - References exam
- `subject_name` (VARCHAR(50), NOT NULL, INDEXED) - Subject (Matematik, Fizik, etc.)
- `total_questions` (INTEGER, NOT NULL) - Questions for this subject
- `correct` (INTEGER, NOT NULL) - Correct answers
- `wrong` (INTEGER, NOT NULL) - Wrong answers
- `blank` (INTEGER, NOT NULL) - Blank answers
- `net_score` (NUMERIC(10,3), NOT NULL) - Subject net score
- `net_percentage` (NUMERIC(5,2), NOT NULL) - Net as percentage
- `class_rank` (INTEGER) - Subject rank in class
- `class_avg` (NUMERIC(10,3)) - Class average for subject
- `school_rank` (INTEGER) - Subject rank in school
- `school_avg` (NUMERIC(10,3)) - School average for subject
- `created_at` (DATETIME) - Record creation

**Relationships:**
- `exam` → Many-to-One with `exams`

**Indexes:**
- `ix_subject_results_exam_id` on `exam_id`
- `ix_subject_results_subject_name` on `subject_name`

---

#### **learning_outcomes**
Topic-level competency tracking (Kazanım Analizi).

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `exam_id` (FK → exams.id, NOT NULL, INDEXED) - References exam
- `subject_name` (VARCHAR(50), NOT NULL, INDEXED) - Subject name
- `category` (VARCHAR(255)) - Main topic category
- `subcategory` (VARCHAR(255)) - Subtopic
- `outcome_description` (TEXT) - Specific learning outcome description
- `total_questions` (INTEGER, NOT NULL) - Questions testing this outcome
- `acquired` (INTEGER, NOT NULL) - Questions answered correctly (Kazanılan)
- `lost` (INTEGER, NOT NULL) - Questions answered incorrectly (Kaybedilen)
- `success_rate` (NUMERIC(5,2)) - Student success percentage
- `student_percentage` (NUMERIC(5,2)) - Student performance
- `class_percentage` (NUMERIC(5,2)) - Class average
- `school_percentage` (NUMERIC(5,2)) - School average
- `merged_into_id` (FK → learning_outcomes.id, INDEXED) - Points to merged target
- `is_merged` (INTEGER, DEFAULT 0) - 0=active, 1=merged
- `created_at` (DATETIME) - Record creation

**Relationships:**
- `exam` → Many-to-One with `exams`
- Self-referencing for merge tracking

**Indexes:**
- `ix_learning_outcomes_exam_id` on `exam_id`
- `ix_learning_outcomes_subject_name` on `subject_name`
- `ix_learning_outcomes_merged_into_id` on `merged_into_id`

**Purpose:** Track fine-grained topic mastery over time. Supports merge operations for duplicate/similar outcomes.

---

#### **questions**
Individual question-level tracking.

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `exam_id` (FK → exams.id, NOT NULL, INDEXED) - References exam
- `subject_name` (VARCHAR(50), NOT NULL, INDEXED) - Subject
- `question_number` (INTEGER, NOT NULL) - Question number in exam
- `correct_answer` (VARCHAR(1)) - Correct option (A, B, C, D, E)
- `student_answer` (VARCHAR(1)) - Student's answer
- `is_correct` (BOOLEAN, DEFAULT FALSE) - Whether answer was correct
- `is_blank` (BOOLEAN, DEFAULT FALSE) - Whether left blank
- `is_canceled` (BOOLEAN, DEFAULT FALSE) - Whether question was canceled (İptal)
- `created_at` (DATETIME) - Record creation

**Relationships:**
- `exam` → Many-to-One with `exams`

**Indexes:**
- `ix_questions_exam_id` on `exam_id`
- `ix_questions_subject_name` on `subject_name`

---

### 3. Recommendations & Study Planning

#### **recommendations**
AI-generated study recommendations based on performance analysis.

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `student_id` (FK → students.id, NOT NULL, INDEXED) - References student
- `generated_at` (DATETIME) - Generation timestamp
- `priority` (INTEGER, NOT NULL) - 1=highest, 5=lowest
- `subject_name` (VARCHAR(50)) - Affected subject
- `topic` (VARCHAR(255)) - Specific topic
- `issue_type` (VARCHAR(50)) - Type: weak_area, blank_pattern, declining_trend, etc.
- `description` (TEXT, NOT NULL) - Human-readable description
- `action_items` (JSON) - Array of specific action steps
- `rationale` (TEXT) - Why this recommendation was made
- `impact_score` (NUMERIC(5,2)) - Estimated impact (0-100)
- `is_active` (BOOLEAN, DEFAULT TRUE) - Whether still relevant
- `learning_outcome_ids` (JSON) - Array of related learning outcome IDs
- `status` (VARCHAR(20), DEFAULT 'new') - Status: new, active, updated, resolved, superseded
- `last_confirmed_at` (DATETIME) - Last reconfirmation timestamp
- `previous_recommendation_id` (FK → recommendations.id) - Link to previous version
- `created_at` (DATETIME) - Record creation

**Relationships:**
- `student` → Many-to-One with `students`
- `previous_recommendation` → Self-referencing for versioning

**Indexes:**
- `ix_recommendations_student_id` on `student_id`

**Purpose:** Track evolution of recommendations over time. Supports intelligent refresh that detects new issues, updates existing ones, and marks resolved issues.

---

#### **study_plans**
Personalized study schedules.

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `student_id` (FK → students.id, NOT NULL, INDEXED) - References student
- `name` (VARCHAR(255), NOT NULL) - Plan name/title
- `time_frame` (INTEGER, NOT NULL) - Duration in days (7, 14, 30)
- `daily_study_time` (INTEGER, NOT NULL) - Minutes per day
- `study_style` (VARCHAR(20), NOT NULL) - Style: intensive, balanced, relaxed
- `status` (VARCHAR(20), DEFAULT 'active', INDEXED) - Status: active, completed, archived
- `start_date` (DATE, NOT NULL) - Plan start date
- `end_date` (DATE, NOT NULL) - Plan end date
- `description` (TEXT) - Optional notes
- `created_at` (DATETIME, NOT NULL) - Creation timestamp
- `updated_at` (DATETIME, NOT NULL) - Last update

**Relationships:**
- `student` → Many-to-One with `students`
- `days` → One-to-Many with `study_plan_days`

**Indexes:**
- `ix_study_plans_student_id` on `student_id`
- `ix_study_plans_status` on `status`

---

#### **study_plan_days**
Daily breakdown within a study plan.

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `plan_id` (FK → study_plans.id, NOT NULL, INDEXED) - References plan
- `day_number` (INTEGER, NOT NULL) - Day number (1-based)
- `date` (DATE, NOT NULL) - Calendar date
- `total_duration_minutes` (INTEGER, DEFAULT 0) - Sum of item durations
- `completed` (BOOLEAN, DEFAULT FALSE, INDEXED) - All items completed?
- `notes` (TEXT) - Optional daily notes

**Relationships:**
- `plan` → Many-to-One with `study_plans`
- `items` → One-to-Many with `study_plan_items`

**Indexes:**
- `ix_study_plan_days_plan_id` on `plan_id`
- `ix_study_plan_days_completed` on `completed`

---

#### **study_plan_items**
Individual study tasks within a day.

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `day_id` (FK → study_plan_days.id, NOT NULL, INDEXED) - References day
- `recommendation_id` (FK → recommendations.id) - Optional link to recommendation
- `subject_name` (VARCHAR(50), NOT NULL) - Subject
- `topic` (VARCHAR(255), NOT NULL) - Topic to study
- `duration_minutes` (INTEGER, NOT NULL) - Time allocation
- `order` (INTEGER, NOT NULL) - Order within day (1, 2, 3...)
- `completed` (BOOLEAN, DEFAULT FALSE, INDEXED) - Completion status
- `completed_at` (DATETIME) - Completion timestamp

**Relationships:**
- `day` → Many-to-One with `study_plan_days`
- `recommendation` → Many-to-One with `recommendations` (optional)

**Indexes:**
- `ix_study_plan_items_day_id` on `day_id`
- `ix_study_plan_items_completed` on `completed`

---

### 4. Curriculum Structure

The curriculum follows a **Subject → Grade → Unit → Topic** hierarchy.

#### **curriculum_subjects**
Top-level subjects (Dersler).

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `subject_name` (VARCHAR(100), NOT NULL, UNIQUE, INDEXED) - Subject name
- `order` (INTEGER, DEFAULT 99) - Display order (lower = higher priority)
- `created_at` (DATETIME) - Record creation

**Relationships:**
- `grades` → One-to-Many with `curriculum_grades`

**Indexes:**
- `ix_curriculum_subjects_subject_name` (UNIQUE) on `subject_name`

**Current Subjects (7):**
1. Türk Dili ve Edebiyatı (order=1)
2. Matematik (order=2)
3. Fizik (order=3)
4. Kimya (order=4)
5. Biyoloji (order=5)
6. Geometri (order=10)
7. Others (order=99)

---

#### **curriculum_grades**
Subject-Grade combinations (Sınıflar).

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `subject_id` (FK → curriculum_subjects.id, NOT NULL, INDEXED) - References subject
- `grade` (VARCHAR(2), NOT NULL, INDEXED) - Grade level ("9", "10", "11", "12")
- `created_at` (DATETIME) - Record creation

**Relationships:**
- `subject` → Many-to-One with `curriculum_subjects`
- `units` → One-to-Many with `curriculum_units`

**Indexes:**
- `ix_curriculum_grades_subject_id` on `subject_id`
- `ix_curriculum_grades_grade` on `grade`

**Total Combinations:** 28 (7 subjects × 4 grades)

---

#### **curriculum_units**
Units within each grade-subject (Üniteler).

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `grade_id` (FK → curriculum_grades.id, NOT NULL, INDEXED) - References grade
- `unit_no` (INTEGER, NOT NULL) - Unit number within grade
- `unit_name` (VARCHAR(255), NOT NULL) - Unit name
- `created_at` (DATETIME) - Record creation

**Relationships:**
- `grade` → Many-to-One with `curriculum_grades`
- `topics` → One-to-Many with `curriculum_topics`

**Indexes:**
- `ix_curriculum_units_grade_id` on `grade_id`

**Total Units:** 112

---

#### **curriculum_topics**
Individual topics within units (Konular).

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `unit_id` (FK → curriculum_units.id, NOT NULL, INDEXED) - References unit
- `topic_name` (VARCHAR(500), NOT NULL) - Topic name/description
- `order` (INTEGER, NOT NULL) - Display order within unit
- `created_at` (DATETIME) - Record creation

**Relationships:**
- `unit` → Many-to-One with `curriculum_units`

**Indexes:**
- `ix_curriculum_topics_unit_id` on `unit_id`

**Total Topics:** 686

---

### 5. Audit & History

#### **outcome_merge_history**
Audit trail for learning outcome merge operations.

**Columns:**
- `id` (PK, VARCHAR(36)) - UUID primary key
- `merge_group_id` (VARCHAR(36), NOT NULL, INDEXED) - Groups related merges
- `merged_at` (DATETIME, NOT NULL) - Merge timestamp
- `merged_by` (VARCHAR(100), DEFAULT 'system') - User/system identifier
- `original_outcome_id` (VARCHAR(36), NOT NULL, INDEXED) - Source outcome
- `target_outcome_id` (VARCHAR(36), NOT NULL, INDEXED) - Destination outcome
- `original_data` (JSON) - Snapshot of original before merge
- `target_data_before` (JSON) - Snapshot of target before merge
- `confidence_score` (NUMERIC(5,2)) - AI confidence (0-100)
- `similarity_reason` (TEXT) - Why these were merged
- `undone_at` (DATETIME) - Undo timestamp (if applicable)
- `undone_by` (VARCHAR(100)) - Who undid the merge
- `created_at` (DATETIME) - Record creation

**Indexes:**
- `ix_outcome_merge_history_merge_group_id` on `merge_group_id`
- `ix_outcome_merge_history_original_outcome_id` on `original_outcome_id`
- `ix_outcome_merge_history_target_outcome_id` on `target_outcome_id`

**Purpose:** Enable undo operations and maintain complete audit trail of merge decisions.

---

## Key Relationships Summary

```
students (1)
├── exams (M)
│   ├── exam_results (1)
│   ├── subject_results (M)
│   ├── learning_outcomes (M)
│   └── questions (M)
├── recommendations (M)
└── study_plans (M)
    └── study_plan_days (M)
        └── study_plan_items (M)

curriculum_subjects (1)
└── curriculum_grades (M)
    └── curriculum_units (M)
        └── curriculum_topics (M)

learning_outcomes
└── merged_into_id (Self-reference for merge tracking)

recommendations
└── previous_recommendation_id (Self-reference for versioning)
```

---

## Database Constraints

### Primary Keys
All tables use UUID (VARCHAR(36)) as primary keys for distributed compatibility and security.

### Foreign Keys
All foreign key relationships enforce referential integrity. Most parent-child relationships use `CASCADE DELETE` for automatic cleanup.

### Unique Constraints
- `exam_results.exam_id` - One result per exam
- `curriculum_subjects.subject_name` - Unique subject names

### Default Values
- Timestamps default to `CURRENT_TIMESTAMP`
- Boolean fields default to `FALSE` or `0`
- Status fields have appropriate defaults ('active', 'confirmed', 'new')
- Numeric fields like `order` default to sensible values

---

## Indexing Strategy

**Purpose-based indexing:**
1. **Foreign keys** - All foreign key columns are indexed for join performance
2. **Filter fields** - Status, completion flags indexed for filtering
3. **Lookup fields** - Names, dates indexed for search operations
4. **Unique fields** - Unique constraints double as indexes

**Total Indexes:** 26 (excluding auto-created primary key indexes)

---

## Data Integrity Features

### Soft Deletes
- **learning_outcomes**: Uses `is_merged` flag instead of hard delete
- **recommendations**: Uses `status='superseded'` for versioning

### Audit Trails
- **outcome_merge_history**: Complete merge operation history
- **recommendations**: Version tracking via `previous_recommendation_id`

### Cascade Rules
- Deleting a student removes all exams, recommendations, and study plans
- Deleting an exam removes all results, outcomes, and questions
- Deleting a study plan removes all days and items

---

## Migration History

All migrations are managed through Alembic:

```bash
# Check current migration
alembic current

# Apply all pending migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

**Latest Migration:** `ffdbec01cad2` - Restructure curriculum schema (Subject→Grade→Unit→Topic hierarchy)

---

## Performance Considerations

### Query Optimization
- Use SQLAlchemy's `joinedload()` for eager loading nested relationships
- Curriculum queries load all 4 levels in single query via eager loading
- Indexes support all common filter and join operations

### Data Volume Estimates (Current)
- **High volume:** questions (702), curriculum_topics (686), learning_outcomes (299)
- **Medium volume:** subject_results (55), curriculum_units (112), curriculum_grades (28)
- **Low volume:** exams (8), recommendations (8), students (1)

### Scaling Considerations
- UUID keys support distributed systems
- JSON columns enable flexible schema evolution
- SQLite suitable for single-user; migrate to PostgreSQL for multi-user

---

## Security Notes

- No passwords stored (authentication out of scope for MVP)
- UUIDs prevent enumeration attacks
- File paths stored securely without exposing system structure
- JSON data validated before storage

---

## Future Enhancements

Potential schema improvements:
1. Add `progress_snapshots` table for historical trend analysis
2. Add `user_sessions` for multi-user support
3. Add `notifications` table for reminders and alerts
4. Add full-text search indexes for curriculum topics
5. Consider partitioning for large-scale data (thousands of exams)

---

**Last Updated:** 2025-11-01
**Schema Version:** ffdbec01cad2
**Database:** SQLite (deneme_analiz.db)
