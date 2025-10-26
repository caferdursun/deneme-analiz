# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Deneme Analiz** - University Exam Preparation Analysis System for Eren Dursun

This is a web-based application that tracks and analyzes mock exam results for a student preparing for Turkish university entrance exams (YKS). The system ingests PDF exam reports, extracts detailed performance data, stores it in a database, and provides comprehensive analytics to track progress and identify areas for improvement.

## Critical Context

### Student Profile
- **Student Name:** Eren Dursun
- **Grade:** 12/B
- **School:** ODTÜ GELİŞTİRME VAKFI ÖZEL LİSESİ
- **Program:** MF (Matematik-Fen / Math-Science track)
- **Goal:** University entrance exam preparation (YKS)

### Exam Structure
Turkish university mock exams (Tarama Sınavı) contain:
- **Matematik** (Mathematics): 32 questions
- **Fizik** (Physics): 14 questions
- **Kimya** (Chemistry): 14 questions
- **Biyoloji** (Biology): 14 questions
- **Türkçe** (Turkish Language): 14 questions

Each exam report PDF contains:
1. Overall scores and rankings (class and school)
2. Per-subject breakdown (correct, wrong, blank answers)
3. Net scores (correct - wrong/4)
4. Comparison graphs (student vs. class vs. school averages)
5. Detailed learning outcome analysis (kazanım analizi)
6. Wrong questions list
7. Blank questions list
8. Topic-specific weaknesses

## Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL
- **PDF Analysis:** Claude API (Anthropic) - uses vision capabilities
- **ORM:** SQLAlchemy
- **Migrations:** Alembic

### Frontend
- **Framework:** React with TypeScript
- **UI Library:** Tailwind CSS + shadcn/ui
- **Charts:** Recharts or Chart.js
- **State Management:** React Query + Context API

### Infrastructure
- **Environment:** Ubuntu (root access)
- **Container:** Docker + Docker Compose (optional, for deployment)
- **API Keys:** Claude API key required (stored in `.env`)

## Development Commands

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database
```bash
# Initialize database
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Running the Application
```bash
# Backend (from backend/)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (from frontend/)
npm install
npm run dev
```

### Testing
```bash
# Backend tests
pytest

# Frontend tests
npm test
```

## Database Schema Overview

### Key Tables
- **students:** Student profile data
- **exams:** Exam metadata (date, name, type)
- **exam_results:** Overall exam performance
- **subject_results:** Per-subject detailed results
- **learning_outcomes:** Topic-level performance (kazanımlar)
- **questions:** Individual question tracking
- **progress_snapshots:** Historical progress data

## Claude API Integration

The system uses Claude API for PDF analysis:
- Endpoint: `POST /api/analyze-pdf`
- Model: Claude 3.5 Sonnet (or latest)
- Input: PDF file upload
- Output: Structured JSON with all exam data

### PDF Analysis Prompt Strategy
The prompt instructs Claude to extract:
1. Student identification
2. Exam metadata
3. Overall scores and rankings
4. Subject-wise detailed breakdown
5. Learning outcome analysis (kazanımlar)
6. Question-level data (correct answers vs. student answers)
7. Weak topics and recommendations

## Key Features

### 1. PDF Upload & Analysis
- Upload exam result PDFs through web interface
- Automatic extraction using Claude Vision API
- Validation and error handling
- Store original PDF for reference

### 2. Performance Tracking
- Overall score trends over time
- Subject-wise progress graphs
- Net score evolution
- Ranking changes (class and school)

### 3. Learning Outcome Analysis
- Track performance by specific topics (kazanımlar)
- Identify consistently weak areas
- Monitor improvement in specific competencies

### 4. Recommendations Engine
- Auto-generate study recommendations based on:
  - Weak subjects
  - Repeated mistakes
  - Blank answer patterns
  - Learning outcome gaps
- Prioritize topics by impact

### 5. Comparative Analytics
- Student vs. class average
- Student vs. school average
- Historical self-comparison

## Important Implementation Notes

### PDF Structure Variations
- Different exam providers may have different PDF formats
- The system should be flexible to handle format variations
- First exam PDF structure (from exam.pdf) is the reference format

### Turkish Language Support
- All subject names, topics, and learning outcomes are in Turkish
- Database should support UTF-8 properly
- Frontend must handle Turkish characters correctly

### Scoring System
- **Net Score Formula:** Correct - (Wrong / 4)
- Blank answers do not affect net score
- Some questions may be marked as "İptal" (canceled) - don't count these

### Learning Outcomes Hierarchy
- Format: `Subject > Topic > Subtopic > Specific Learning Outcome`
- Each level has success percentage
- Track both "Kazanılan" (acquired) and "Kaybedilen" (lost) competencies

## Development Priorities

1. **Phase 1:** Core PDF analysis + database setup
2. **Phase 2:** Basic web interface for upload
3. **Phase 3:** Dashboard with progress visualization
4. **Phase 4:** Advanced analytics and recommendations
5. **Phase 5:** Mobile responsiveness and UX improvements

## File Structure
```
/root/projects/deneme-analiz/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   └── utils/    # Helpers (Claude API client)
│   ├── alembic/      # Database migrations
│   └── requirements.txt
├── frontend/         # React application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   └── package.json
├── data/            # Uploaded PDFs storage
├── docs/            # Additional documentation
├── CLAUDE.md        # This file
├── ARCHITECTURE.md  # System design
├── PLAN.md          # Development roadmap
├── PROGRESS.md      # Implementation tracking
└── .env.example     # Environment variables template
```

## Environment Variables
```
# Claude API
ANTHROPIC_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/deneme_analiz

# Application
SECRET_KEY=your_secret_key
DEBUG=True
```

## Common Debugging Tips

- If PDF analysis fails, check Claude API key and quota
- Turkish character issues: Ensure database uses UTF-8 encoding
- For slow queries, check database indexes on frequently queried fields
- Always validate extracted data before database insertion

## Next Steps for New Claude Instances

1. Review PROGRESS.md to see current implementation status
2. Check open TODOs in PLAN.md
3. Review recent git commits (if initialized)
4. Test current functionality before making changes
