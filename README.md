# Deneme Analiz - University Exam Tracker

A comprehensive web application for tracking and analyzing university entrance exam preparation progress.

## 📋 Project Overview

This system helps students prepare for Turkish university entrance exams (YKS) by:
- Uploading and analyzing exam result PDFs
- Tracking progress over time
- Identifying weak areas and topics
- Providing personalized study recommendations
- Visualizing performance trends

**Current Student**: Eren Dursun (12th Grade, Math-Science Track)

## 🏗️ Architecture

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React with TypeScript
- **Database**: PostgreSQL / SQLite
- **AI Analysis**: Claude API (Anthropic)

## 📚 Documentation

- **[CLAUDE.md](./CLAUDE.md)** - Project context for AI assistants
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Detailed system design
- **[PLAN.md](./PLAN.md)** - Development roadmap
- **[PROGRESS.md](./PROGRESS.md)** - Implementation progress tracker

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (optional, SQLite works for development)
- Anthropic API key

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Initialize database
alembic upgrade head

# Run the server
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

## 🎯 Features

### Current (MVP)
- PDF upload and analysis
- Exam result storage
- Basic dashboard

### Planned
- Interactive analytics dashboard
- Subject-wise progress tracking
- Learning outcome analysis
- AI-powered study recommendations
- Comparative analytics
- Export functionality

## 📊 Exam Structure

Turkish university mock exams contain:
- **Matematik** (Mathematics): 32 questions
- **Fizik** (Physics): 14 questions
- **Kimya** (Chemistry): 14 questions
- **Biyoloji** (Biology): 14 questions
- **Türkçe** (Turkish): 14 questions

Each PDF contains detailed performance data, rankings, and learning outcome analysis.

## 🛠️ Development

### Project Structure
```
deneme-analiz/
├── backend/          # FastAPI application
├── frontend/         # React application
├── data/            # Uploaded PDFs
├── docs/            # Additional documentation
└── exam.pdf         # Sample exam result
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📝 License

Private project for personal use.

## 🤝 Contributing

This is a personal project. Not open for external contributions at this time.

## 📧 Contact

For questions or support, please refer to the project documentation.

---

**Last Updated**: 2025-10-26
**Status**: In Development - Phase 1
