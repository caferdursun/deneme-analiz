# Entity-Relationship Diagram

## Database Schema Visual Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DENEME ANALİZ DATABASE                             │
│                      University Exam Analysis System                         │
└─────────────────────────────────────────────────────────────────────────────┘


╔═══════════════════════════════════════════════════════════════════════════╗
║                         1. CORE IDENTITY & EXAMS                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌──────────────────┐
│    STUDENTS      │
│ ──────────────── │
│ • id (PK)        │
│   name           │◄───────────────┐
│   school         │                │
│   grade          │                │ 1:M
│   class_section  │                │
│   program        │                │
│   created_at     │                │
│   updated_at     │                │
└──────────────────┘                │
         ▲                          │
         │ 1:M                      │
         │                          │
         │                    ┌─────┴────────────┐
         │                    │      EXAMS       │
         │                    │ ──────────────── │
         │                    │ • id (PK)        │
         │                    │   student_id (FK)│
         │                    │   exam_name      │
         │                    │   exam_date      │
         │                    │   booklet_type   │
         │                    │   pdf_path       │
         │                    │   status         │
         │                    │   claude_data    │
         │                    │   local_data     │
         │                    │   validation_rpt │
         │                    │   uploaded_at    │
         │                    │   processed_at   │
         │                    │   confirmed_at   │
         │                    └──────────────────┘
         │                             │
         │                             │ 1:M
         │           ┌─────────────────┼─────────────────┬─────────────────┐
         │           │                 │                 │                 │
         │      ┌────┴──────┐   ┌──────┴────────┐  ┌────┴─────────┐  ┌───┴─────────┐
         │      │   EXAM    │   │   SUBJECT     │  │  LEARNING    │  │  QUESTIONS  │
         │      │  RESULTS  │   │   RESULTS     │  │  OUTCOMES    │  │             │
         │      │ ───────── │   │ ───────────── │  │ ──────────── │  │ ─────────── │
         │      │ • id (PK) │   │ • id (PK)     │  │ • id (PK)    │  │ • id (PK)   │
         │      │ exam_id(FK)│   │ exam_id (FK) │  │ exam_id (FK) │  │ exam_id(FK) │
         │      │ total_q   │   │ subject_name  │  │ subject_name │  │ subject_name│
         │      │ correct   │   │ total_q       │  │ category     │  │ question_no │
         │      │ wrong     │   │ correct       │  │ subcategory  │  │ correct_ans │
         │      │ blank     │   │ wrong         │  │ outcome_desc │  │ student_ans │
         │      │ net_score │   │ blank         │  │ total_q      │  │ is_correct  │
         │      │ net_%     │   │ net_score     │  │ acquired     │  │ is_blank    │
         │      │ class_rank│   │ net_%         │  │ lost         │  │ is_canceled │
         │      │ school_rk │   │ class_rank    │  │ success_%    │  └─────────────┘
         │      │ class_avg │   │ class_avg     │  │ class_%      │
         │      │ school_avg│   │ school_rank   │  │ school_%     │
         │      └───────────┘   │ school_avg    │  │ merged_into  │◄──┐
         │                      └───────────────┘  │ is_merged    │   │ Self-ref
         │                                         └──────────────┘   │ (Merge)
         │                                                  │          │
         │                                                  └──────────┘
         │
         │
╔═══════════════════════════════════════════════════════════════════════════╗
║                    2. RECOMMENDATIONS & STUDY PLANS                        ║
╚═══════════════════════════════════════════════════════════════════════════╝
         │
         │ 1:M
         │
    ┌────┴────────────────┐
    │  RECOMMENDATIONS    │◄──────┐
    │ ─────────────────── │       │ Self-ref
    │ • id (PK)           │       │ (Versioning)
    │   student_id (FK)   │       │
    │   generated_at      │       │
    │   priority          │       │
    │   subject_name      │       │
    │   topic             │       │
    │   issue_type        │       │
    │   description       │       │
    │   action_items      │       │
    │   rationale         │       │
    │   impact_score      │       │
    │   is_active         │       │
    │   learning_out_ids  │       │
    │   status            │       │
    │   last_confirmed_at │       │
    │   prev_rec_id (FK)  ├───────┘
    └─────────────────────┘
              │
              │ M:M (via study_plan_items)
              │
         ┌────┴─────────────┐
         │   STUDY PLANS    │
         │ ──────────────── │
         │ • id (PK)        │
         │   student_id (FK)│◄─── 1:M ────┐
         │   name           │              │
         │   time_frame     │              │
         │   daily_study_t  │              │
         │   study_style    │              │
         │   status         │              │
         │   start_date     │              │
         │   end_date       │              │
         │   description    │              │
         └──────────────────┘              │
                  │ 1:M                    │
                  │                        │
         ┌────────┴───────────┐            │
         │ STUDY PLAN DAYS    │            │
         │ ────────────────── │            │
         │ • id (PK)          │            │
         │   plan_id (FK)     │            │
         │   day_number       │            │
         │   date             │            │
         │   total_duration   │            │
         │   completed        │            │
         │   notes            │            │
         └────────────────────┘            │
                  │ 1:M                    │
                  │                        │
         ┌────────┴───────────┐            │
         │ STUDY PLAN ITEMS   │            │
         │ ────────────────── │            │
         │ • id (PK)          │            │
         │   day_id (FK)      │            │
         │   rec_id (FK, opt) │            │
         │   subject_name     │            │
         │   topic            │            │
         │   duration_mins    │            │
         │   order            │            │
         │   completed        │            │
         │   completed_at     │            │
         └────────────────────┘            │
                                           │
                                           │
╔═══════════════════════════════════════════════════════════════════════════╗
║                        3. CURRICULUM HIERARCHY                             ║
╚═══════════════════════════════════════════════════════════════════════════╝

         ┌──────────────────────┐
         │ CURRICULUM SUBJECTS  │  ◄─── Top Level: 7 subjects
         │ ──────────────────── │       (Türkçe, Matematik, etc.)
         │ • id (PK)            │
         │   subject_name (UQ)  │
         │   order              │
         │   created_at         │
         └──────────────────────┘
                  │ 1:M
                  │
         ┌────────┴─────────────┐
         │ CURRICULUM GRADES    │  ◄─── Level 2: Grade levels
         │ ──────────────────── │       (28 combinations: 7×4)
         │ • id (PK)            │       9th, 10th, 11th, 12th
         │   subject_id (FK)    │
         │   grade              │
         │   created_at         │
         └──────────────────────┘
                  │ 1:M
                  │
         ┌────────┴─────────────┐
         │ CURRICULUM UNITS     │  ◄─── Level 3: Units
         │ ──────────────────── │       (112 total units)
         │ • id (PK)            │
         │   grade_id (FK)      │
         │   unit_no            │
         │   unit_name          │
         │   created_at         │
         └──────────────────────┘
                  │ 1:M
                  │
         ┌────────┴─────────────┐
         │ CURRICULUM TOPICS    │  ◄─── Level 4: Topics
         │ ──────────────────── │       (686 total topics)
         │ • id (PK)            │
         │   unit_id (FK)       │
         │   topic_name         │
         │   order              │
         │   created_at         │
         └──────────────────────┘


╔═══════════════════════════════════════════════════════════════════════════╗
║                          4. AUDIT & HISTORY                                ║
╚═══════════════════════════════════════════════════════════════════════════╝

         ┌───────────────────────────┐
         │ OUTCOME MERGE HISTORY     │  ◄─── Tracks learning outcome merges
         │ ───────────────────────── │
         │ • id (PK)                 │
         │   merge_group_id          │
         │   merged_at               │
         │   merged_by               │
         │   original_outcome_id     │
         │   target_outcome_id       │
         │   original_data (JSON)    │
         │   target_data_before(JSON)│
         │   confidence_score        │
         │   similarity_reason       │
         │   undone_at               │
         │   undone_by               │
         │   created_at              │
         └───────────────────────────┘


═══════════════════════════════════════════════════════════════════════════

LEGEND:
  │   = One-to-Many relationship
  ◄─  = Foreign Key reference
  (PK)  = Primary Key
  (FK)  = Foreign Key
  (UQ)  = Unique constraint
  1:M   = One-to-Many
  M:M   = Many-to-Many

═══════════════════════════════════════════════════════════════════════════
```

## Relationship Summary

### Primary Data Flow

```
Student Profile
    ↓
Uploads Exam PDF
    ↓
System extracts data → Creates Exam Record
    ↓
Generates:
    • Overall Exam Result (1)
    • Subject Results (5-7 per exam)
    • Learning Outcomes (30-50 per exam)
    • Questions (70-90 per exam)
    ↓
AI analyzes performance
    ↓
Generates Recommendations (based on weak areas)
    ↓
Student selects recommendations
    ↓
System generates Study Plan
    ↓
Study Plan broken into Days
    ↓
Each Day contains Study Items
    ↓
Student tracks progress
```

### Curriculum Flow

```
Curriculum Subjects (7)
    ↓
Each has 4 Grade levels (28 total)
    ↓
Each Grade-Subject has multiple Units (112 total)
    ↓
Each Unit contains Topics (686 total)
```

### Key Cascading Delete Rules

1. **Delete Student** → Deletes all exams, recommendations, study plans
2. **Delete Exam** → Deletes exam results, subject results, outcomes, questions
3. **Delete Study Plan** → Deletes all days and items
4. **Delete Curriculum Subject** → Deletes all grades, units, topics

### Soft Delete Patterns

- **Learning Outcomes**: `is_merged=1` instead of hard delete
- **Recommendations**: `status='superseded'` for versioning
- **Study Plans**: `status='archived'` for history

## Index Coverage

All foreign keys are indexed for optimal join performance:
- 26 explicit indexes
- All primary keys auto-indexed
- Strategic indexes on filter fields (status, completed, dates)

## Data Volume Guidelines

**Current State (Nov 2025):**
- Students: 1
- Exams: 8
- Questions: 702
- Learning Outcomes: 299
- Curriculum Topics: 686

**Expected Growth Pattern:**
- ~10-15 exams per year per student
- ~700-1000 questions per year
- ~300-500 learning outcomes per year
- Recommendations refresh weekly/monthly
- Study plans created monthly

**Scaling Notes:**
- SQLite suitable for <10,000 exams
- Consider PostgreSQL at 1000+ students
- Partition strategy needed at 100K+ exams
