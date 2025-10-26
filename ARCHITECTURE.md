# System Architecture

## Overview

Deneme Analiz is a three-tier web application designed to analyze and track university entrance exam preparation progress. The system processes PDF exam reports, stores structured data, and provides analytics and recommendations.

## High-Level Architecture

```
┌─────────────────┐
│   Web Browser   │
│   (Frontend)    │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   React App     │
│   (SPA)         │
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐      ┌──────────────┐
│   FastAPI       │─────▶│  Claude API  │
│   Backend       │      │  (Anthropic) │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│   PostgreSQL    │      │  File System │
│   Database      │      │  (PDF Store) │
└─────────────────┘      └──────────────┘
```

## Component Details

### 1. Frontend Layer (React + TypeScript)

#### Responsibilities
- User interface for PDF upload
- Display exam results and analytics
- Interactive charts and visualizations
- Progress tracking dashboard
- Recommendations display

#### Key Components

##### Pages
- **Dashboard**: Overview of all exams and progress trends
- **Upload**: PDF upload interface with drag-and-drop
- **Exam Detail**: Single exam deep-dive analysis
- **Subject Analysis**: Per-subject progress tracking
- **Learning Outcomes**: Topic-level performance analysis
- **Recommendations**: AI-generated study suggestions

##### Shared Components
- **ExamCard**: Display summary of single exam
- **ScoreChart**: Visualize score trends
- **SubjectBreakdown**: Pie/bar charts for subject performance
- **ComparisonGraph**: Student vs. class vs. school
- **TopicTree**: Hierarchical learning outcomes display
- **ProgressIndicator**: Visual progress bars
- **RecommendationCard**: Study recommendation display

#### State Management
- **React Query**: Server state (API calls, caching)
- **Context API**: Global UI state (theme, user settings)
- **Local State**: Component-specific state

#### Routing
```
/                    → Dashboard
/upload              → PDF Upload
/exams/:examId       → Exam Detail
/subjects/:subject   → Subject Analysis
/learning-outcomes   → Learning Outcomes Analysis
/recommendations     → Study Recommendations
```

### 2. Backend Layer (FastAPI + Python)

#### Responsibilities
- RESTful API endpoints
- PDF processing and analysis
- Business logic and data validation
- Database operations
- Claude API integration
- Recommendation generation

#### API Endpoints

##### Exam Management
```
POST   /api/exams/upload          → Upload and process PDF
GET    /api/exams                 → List all exams
GET    /api/exams/{exam_id}       → Get exam details
DELETE /api/exams/{exam_id}       → Delete exam
GET    /api/exams/{exam_id}/pdf   → Download original PDF
```

##### Analytics
```
GET /api/analytics/overview        → Overall progress summary
GET /api/analytics/subjects        → Subject-wise analytics
GET /api/analytics/trends          → Score trends over time
GET /api/analytics/comparisons     → Comparative analytics
GET /api/analytics/learning-outcomes → Learning outcome analysis
```

##### Recommendations
```
GET /api/recommendations           → Get study recommendations
POST /api/recommendations/refresh  → Regenerate recommendations
```

##### Student
```
GET /api/student                   → Get student profile
PUT /api/student                   → Update student profile
```

#### Service Layer Architecture

```
app/
├── api/
│   ├── routes/
│   │   ├── exams.py              # Exam endpoints
│   │   ├── analytics.py          # Analytics endpoints
│   │   ├── recommendations.py     # Recommendation endpoints
│   │   └── student.py             # Student endpoints
│   └── dependencies.py            # Shared dependencies
├── models/
│   ├── student.py
│   ├── exam.py
│   ├── subject_result.py
│   ├── learning_outcome.py
│   ├── question.py
│   └── recommendation.py
├── schemas/
│   ├── exam.py                    # Pydantic request/response models
│   ├── analytics.py
│   └── recommendation.py
├── services/
│   ├── pdf_analyzer.py            # Claude API integration
│   ├── exam_service.py            # Exam business logic
│   ├── analytics_service.py       # Analytics calculations
│   └── recommendation_service.py  # Recommendation engine
├── utils/
│   ├── claude_client.py           # Claude API client
│   ├── pdf_utils.py               # PDF handling utilities
│   └── validators.py              # Data validation
├── core/
│   ├── config.py                  # Configuration management
│   ├── database.py                # Database connection
│   └── security.py                # Security utilities
└── main.py                        # Application entry point
```

### 3. Database Layer (PostgreSQL)

#### Schema Design

##### Core Tables

**students**
```sql
id              UUID PRIMARY KEY
name            VARCHAR(255) NOT NULL
school          VARCHAR(255)
grade           VARCHAR(10)
class_section   VARCHAR(10)
program         VARCHAR(10)  -- MF, TM, etc.
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**exams**
```sql
id              UUID PRIMARY KEY
student_id      UUID REFERENCES students(id)
exam_name       VARCHAR(255) NOT NULL
exam_date       DATE NOT NULL
booklet_type    VARCHAR(10)  -- A, B, C, D
exam_number     INTEGER
pdf_path        VARCHAR(500)
uploaded_at     TIMESTAMP
processed_at    TIMESTAMP
created_at      TIMESTAMP
```

**exam_results**
```sql
id              UUID PRIMARY KEY
exam_id         UUID REFERENCES exams(id)
total_questions INTEGER
total_correct   INTEGER
total_wrong     INTEGER
total_blank     INTEGER
net_score       DECIMAL(10,3)
net_percentage  DECIMAL(5,2)
class_rank      INTEGER
class_total     INTEGER
school_rank     INTEGER
school_total    INTEGER
class_avg       DECIMAL(10,3)
school_avg      DECIMAL(10,3)
created_at      TIMESTAMP
```

**subject_results**
```sql
id              UUID PRIMARY KEY
exam_id         UUID REFERENCES exams(id)
subject_name    VARCHAR(50) NOT NULL
total_questions INTEGER
correct         INTEGER
wrong           INTEGER
blank           INTEGER
net_score       DECIMAL(10,3)
net_percentage  DECIMAL(5,2)
class_rank      INTEGER
class_avg       DECIMAL(10,3)
school_rank     INTEGER
school_avg      DECIMAL(10,3)
created_at      TIMESTAMP
```

**learning_outcomes**
```sql
id                  UUID PRIMARY KEY
exam_id             UUID REFERENCES exams(id)
subject_name        VARCHAR(50) NOT NULL
category            VARCHAR(255)  -- Main category
subcategory         VARCHAR(255)  -- Subcategory
outcome_description TEXT          -- Specific learning outcome
total_questions     INTEGER
acquired            INTEGER       -- Kazanılan
lost                INTEGER       -- Kaybedilen
success_rate        DECIMAL(5,2)
student_percentage  DECIMAL(5,2)
class_percentage    DECIMAL(5,2)
school_percentage   DECIMAL(5,2)
created_at          TIMESTAMP
```

**questions**
```sql
id              UUID PRIMARY KEY
exam_id         UUID REFERENCES exams(id)
subject_name    VARCHAR(50) NOT NULL
question_number INTEGER NOT NULL
correct_answer  VARCHAR(1)
student_answer  VARCHAR(1)
is_correct      BOOLEAN
is_blank        BOOLEAN
is_canceled     BOOLEAN
created_at      TIMESTAMP
```

**recommendations**
```sql
id              UUID PRIMARY KEY
student_id      UUID REFERENCES students(id)
generated_at    TIMESTAMP
priority        INTEGER  -- 1=highest, 5=lowest
subject_name    VARCHAR(50)
topic           VARCHAR(255)
issue_type      VARCHAR(50)  -- weak_area, blank_pattern, etc.
description     TEXT
action_items    JSONB  -- Array of specific actions
rationale       TEXT   -- Why this recommendation
impact_score    DECIMAL(5,2)  -- Estimated impact
is_active       BOOLEAN
created_at      TIMESTAMP
```

#### Indexes

```sql
-- Performance optimization
CREATE INDEX idx_exams_student_date ON exams(student_id, exam_date DESC);
CREATE INDEX idx_subject_results_exam_subject ON subject_results(exam_id, subject_name);
CREATE INDEX idx_learning_outcomes_exam_subject ON learning_outcomes(exam_id, subject_name);
CREATE INDEX idx_questions_exam_subject ON questions(exam_id, subject_name);
CREATE INDEX idx_recommendations_student_active ON recommendations(student_id, is_active);
```

### 4. External Services

#### Claude API (Anthropic)

**Purpose**: PDF analysis and text extraction

**Integration Pattern**:
1. Receive PDF file from frontend
2. Convert PDF to base64 or multipart upload
3. Send to Claude API with structured extraction prompt
4. Parse JSON response
5. Validate extracted data
6. Store in database

**Prompt Engineering Strategy**:
```python
system_prompt = """
You are an expert at analyzing Turkish university entrance exam reports.
Extract all information from the PDF in the exact JSON format specified.
Pay attention to Turkish characters and numerical data accuracy.
"""

user_prompt = """
Analyze this exam report PDF and extract the following information:
1. Student identification (name, school, class)
2. Exam metadata (name, date, booklet type)
3. Overall performance scores and rankings
4. Subject-wise detailed breakdown
5. Learning outcomes analysis with all subcategories
6. Question-by-question comparison (correct vs. student answers)
7. Lists of wrong questions and blank questions

Return as JSON with this structure:
{
  "student": {...},
  "exam": {...},
  "overall_results": {...},
  "subjects": [...],
  "learning_outcomes": [...],
  "questions": [...]
}
"""
```

**Error Handling**:
- Retry logic for transient failures
- Validation of extracted data
- Fallback to manual entry if analysis fails
- Store raw Claude response for debugging

### 5. Data Flow

#### PDF Upload Flow

```
1. User uploads PDF
   ↓
2. Frontend validates file (type, size)
   ↓
3. POST /api/exams/upload
   ↓
4. Backend saves PDF to file system
   ↓
5. Claude API analyzes PDF
   ↓
6. Backend validates extracted data
   ↓
7. Store in database (transaction)
   ↓
8. Trigger recommendation generation
   ↓
9. Return exam ID to frontend
   ↓
10. Frontend redirects to exam detail page
```

#### Analytics Calculation Flow

```
1. Request for analytics
   ↓
2. Backend queries relevant exams
   ↓
3. Calculate trends and aggregations
   ↓
4. Compare with class/school averages
   ↓
5. Identify patterns (improving/declining subjects)
   ↓
6. Cache results (5 minutes)
   ↓
7. Return formatted data
   ↓
8. Frontend renders charts
```

#### Recommendation Generation Flow

```
1. Triggered after new exam or manual refresh
   ↓
2. Fetch all exam data for student
   ↓
3. Analyze patterns:
   - Consistently weak subjects
   - Topics with high blank rates
   - Learning outcomes with low success
   - Declining trends
   ↓
4. Score each potential recommendation by impact
   ↓
5. Generate action items using Claude API
   ↓
6. Store recommendations (deactivate old ones)
   ↓
7. Return top 10 recommendations
```

## Security Considerations

### Authentication (Future Phase)
- JWT-based authentication
- Session management
- Password hashing with bcrypt

### Authorization
- Row-level security (student can only see their data)
- Admin role for teachers/mentors

### Data Protection
- HTTPS only
- API rate limiting
- SQL injection prevention (parameterized queries)
- XSS protection (sanitize inputs)
- CORS configuration

### API Key Management
- Claude API key stored in environment variables
- Never expose in frontend
- Rotate keys periodically

## Scalability Considerations

### Current Design (Single Student)
- Simple deployment
- SQLite or PostgreSQL
- Single server

### Future Scaling (Multiple Students)
- Database connection pooling
- Redis for caching
- Background job queue (Celery) for PDF processing
- CDN for static assets
- Horizontal scaling with load balancer

## Monitoring and Logging

### Logging Strategy
- Request/response logging
- Error tracking (Sentry)
- Performance metrics
- Claude API usage tracking

### Health Checks
- `/health` endpoint
- Database connectivity
- Claude API availability
- Disk space monitoring

## Deployment Architecture

### Development
```
Local machine
├── Backend: http://localhost:8000
├── Frontend: http://localhost:3000
└── Database: localhost:5432
```

### Production (Simple)
```
Single Ubuntu Server
├── Nginx (reverse proxy)
├── FastAPI (uvicorn/gunicorn)
├── PostgreSQL
└── React (static build)
```

### Production (Advanced - Future)
```
Cloud Infrastructure
├── Load Balancer
├── Application Servers (N)
├── Database (RDS/managed)
├── Object Storage (S3) for PDFs
└── CDN for frontend
```

## Technology Justification

### Why FastAPI?
- Modern, fast Python framework
- Automatic OpenAPI documentation
- Native async support
- Excellent for AI/ML integration
- Type safety with Pydantic

### Why PostgreSQL?
- Robust relational database
- JSON support for flexible data
- Strong consistency
- Good performance for analytics queries

### Why React?
- Component-based architecture
- Rich ecosystem
- Good charting libraries
- TypeScript support

### Why Claude API?
- Best-in-class vision capabilities
- Excellent for structured extraction
- Reliable JSON output
- Handles Turkish text well

## Future Enhancements

1. **Multi-user Support**: Add authentication and multiple students
2. **Real-time Updates**: WebSocket for live data updates
3. **Mobile App**: React Native mobile application
4. **Export Features**: PDF reports, Excel exports
5. **Study Planner**: Integrate recommendations with calendar
6. **Question Bank**: Store and review individual questions
7. **AI Tutor**: Chat interface for study help using Claude
8. **Comparison Groups**: Compare with peers anonymously
9. **Predictive Analytics**: ML models for success prediction
10. **Integration**: Connect with official exam systems
