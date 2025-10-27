# 📚 Study Plan Generator - Detaylı Sub-Phase Breakdown

## Genel Bakış
Study Plan Generator, öğrencinin aktif önerilerinden otomatik ve kişiselleştirilmiş çalışma programları oluşturur. Claude AI desteğiyle akıllı zamanlama ve konu dağılımı yapar.

---

## Phase 2.1.1: Database Schema & Backend Models (Foundation)
**Süre: ~1 saat**
**Durum: [✅] TAMAMLANDI**

### Görevler:
- [✅] `StudyPlan` model oluştur
  - Alanlar: id, student_id, name, time_frame, daily_study_time, study_style, status, start_date, end_date, created_at, updated_at
  - Status: 'active', 'completed', 'archived'
  - Time frame: 7, 14, 30 (days)
  - Study style: 'intensive', 'balanced', 'relaxed'

- [✅] `StudyPlanDay` model oluştur
  - Alanlar: id, plan_id, day_number, date, total_duration_minutes, completed, notes
  - İlişki: belongs_to StudyPlan

- [✅] `StudyPlanItem` model oluştur
  - Alanlar: id, day_id, recommendation_id, subject_name, topic, description, duration_minutes, order, completed, completed_at
  - İlişki: belongs_to StudyPlanDay, belongs_to Recommendation

- [✅] Alembic migration oluştur ve uygula
  - Foreign key constraints
  - Indexes (student_id, status, date)

- [✅] Model relationships tanımla
  - StudyPlan.days (one-to-many)
  - StudyPlanDay.items (one-to-many)
  - StudyPlanItem.recommendation (many-to-one)

### Beklenen Çıktı: ✅ TAMAMLANDI
- ✅ 3 yeni model dosyası: `study_plan.py`, `study_plan_day.py`, `study_plan_item.py`
- ✅ 1 migration dosyası: `9bad78e712dc_add_study_plan_tables.py`
- ✅ Models __init__.py güncellendi
- ✅ Student model'e study_plans relationship eklendi
- ✅ Database tabloları oluşturuldu ve doğrulandı

---

## Phase 2.1.2: Backend API - Configuration & Generation (Core Logic)
**Süre: ~2-3 saat**
**Durum: [✅] TAMAMLANDI**

### Görevler:
- [✅] Pydantic schemas oluştur
  - StudyPlanGenerateRequest (input)
  - StudyPlanResponse (output)
  - StudyPlanDayResponse
  - StudyPlanItemResponse
  - StudyPlanProgressResponse
  - UpdateItemCompletionRequest

- [✅] `StudyPlanService` oluştur
  - `generate_study_plan()` - Claude AI ile plan oluşturma
  - `get_study_plan()` - Plan detaylarını getir
  - `get_active_plan()` - Aktif planı getir
  - `update_item_completion()` - Item tamamlama durumunu güncelle
  - `calculate_progress()` - İlerleme hesapla

- [✅] Claude AI Prompt Engineering
  - Input: recommendations, time_frame, daily_study_time, study_style
  - Mantık: Impact score prioritization, subject balance, review sessions
  - Output: Günlük çalışma planı (JSON)
  - Model: claude-sonnet-4-20250514

- [✅] API endpoints oluştur
  - POST `/api/study-plans/generate`
  - GET `/api/study-plans/{id}`
  - GET `/api/study-plans/active/current`
  - GET `/api/study-plans` (list)
  - PUT `/api/study-plans/{id}/items/{item_id}/complete`
  - GET `/api/study-plans/{id}/progress`
  - PUT `/api/study-plans/{id}/archive`
  - DELETE `/api/study-plans/{id}`

- [✅] Router'ı main.py'a ekle

### Beklenen Çıktı: ✅ TAMAMLANDI
- ✅ `backend/app/services/study_plan_service.py` - Claude AI integration ile service
- ✅ `backend/app/schemas/study_plan.py` - Complete Pydantic schemas
- ✅ `backend/app/api/routes/study_plans.py` - 8 endpoint ile router
- ✅ main.py'a router eklendi
- ✅ API endpoints test edildi ve çalışıyor

---

## Phase 2.1.3: Frontend Wizard Component (User Interface)
**Süre: ~2-3 saat**
**Durum: [✅] TAMAMLANDI**

### Görevler:
- [✅] StudyPlanWizardPage component oluştur
  - Multi-step form (5 steps)
  - Step navigation (back, next, submit)
  - Form validation

- [✅] Step 1: Plan Name & Time Frame Selection
  - Plan adı input field
  - Radio buttons: 1 Hafta / 2 Hafta / 1 Ay
  - Visual cards with descriptions

- [✅] Step 2: Topic Selection
  - Aktif recommendations'dan seçim
  - Checkbox list with subject badges
  - "Hepsini Seç" / "Temizle" buttons
  - Selected count display

- [✅] Step 3: Daily Study Time
  - Radio buttons: 1 saat / 2 saat / 3 saat / 4 saat
  - Custom time input (slider 30-480 dakika)
  - Real-time duration display

- [✅] Step 4: Study Style
  - Radio cards: Yoğun / Dengeli / Rahat
  - Emojis and detailed descriptions
  - Full-width cards with icons

- [✅] Step 5: Preview & Confirm
  - Seçilen parametrelerin özeti
  - Subject-wise breakdown
  - "Plan Oluştur" button
  - Claude AI integration notice

- [✅] API client methods ekle
  - `studyPlansAPI.generate()`
  - `studyPlansAPI.getActive()`
  - `studyPlansAPI.getById()`
  - `studyPlansAPI.list()`
  - `studyPlansAPI.updateItemCompletion()`
  - `studyPlansAPI.getProgress()`
  - `studyPlansAPI.archive()`
  - `studyPlansAPI.delete()`

### Beklenen Çıktı: ✅ TAMAMLANDI
- ✅ `frontend/src/pages/StudyPlanWizardPage.tsx` - Complete 5-step wizard
- ✅ TypeScript types added to `frontend/src/types/index.ts`
- ✅ API client methods in `frontend/src/api/client.ts`
- ✅ Route `/study-plan/create` added to App.tsx
- ✅ Progress indicator with step labels
- ✅ Error handling and loading states
- ✅ Subject color coding integration

---

## Phase 2.1.4: Calendar View & Display (Visualization)
**Süre: ~2 saat**
**Durum: [✅] TAMAMLANDI**

### Görevler:
- [✅] StudyPlanPage component oluştur
  - Plan header (name, dates, progress)
  - Calendar grid view
  - Integrated day detail card

- [✅] Calendar component
  - 7-column grid layout for all days
  - Day cells showing day number and date
  - Color coding for status (today, past, completed, selected)
  - Visual indicators for completed days

- [✅] DayDetailCard component
  - Sticky card showing selected day details
  - Item list with checkboxes
  - Duration display per item
  - Subject badges with colors
  - Completion tracking with timestamps

- [✅] Progress indicator
  - Overall progress bar with percentage
  - On-track status indicator
  - Completed items / total items counter
  - Days remaining display
  - Warning message if behind schedule

### Beklenen Çıktı: ✅ TAMAMLANDI
- ✅ `frontend/src/pages/StudyPlanPage.tsx` - Complete calendar and detail view
- ✅ Route `/study-plan/:planId` added to App.tsx
- ✅ Real-time item completion toggle
- ✅ Progress calculation and display
- ✅ Today/past/future day highlighting
- ✅ Subject color coding integration
- ✅ Responsive grid layout

---

## Phase 2.1.5: Progress Tracking (Interaction)
**Süre: ~1-2 saat**
**Durum: [✅] TAMAMLANDI**

### Görevler:
- [✅] Item completion toggle
  - Checkbox onClick handler (StudyPlanPage'de zaten mevcut)
  - Optimistic UI update
  - API call to mark complete/incomplete

- [✅] Progress calculation
  - Item level: completed count / total count
  - Day level: all items completed
  - Plan level: overall percentage
  - Backend'de calculate_progress endpoint

- [✅] Visual feedback
  - Checked items strikethrough
  - Completed days badge
  - Progress bar with color coding
  - On-track status indicator

- [✅] Today's tasks section
  - Dashboard widget showing today's items
  - Quick complete from dashboard
  - Subject badges and duration display
  - Link to full study plan

- [✅] Dashboard Integration
  - "Çalışma Planı" button (shows "Planım" if active plan exists)
  - "Bugünün Görevleri" widget
  - Active plan detection
  - Task completion from dashboard

### Beklenen Çıktı: ✅ TAMAMLANDI
- ✅ StudyPlanPage with completion logic (implemented in Phase 2.1.4)
- ✅ Dashboard widget for today's tasks
- ✅ Real-time progress updates
- ✅ Quick task completion from dashboard
- ✅ Dynamic button (Create vs View Plan)

---

## Phase 2.1.6: Management & Export (Advanced Features)
**Süre: ~2-3 saat**
**Durum: [ ] Başlanmadı**

### Görevler:
- [ ] Study Plans List page
  - Active plans
  - Completed plans
  - Archived plans
  - Create new button

- [ ] Plan management
  - Edit plan (change duration, topics)
  - Archive plan
  - Delete plan
  - Duplicate plan

- [ ] PDF Export
  - Formatted weekly schedule
  - Subject breakdown
  - Progress summary
  - Print-friendly layout

- [ ] CSV Export
  - Day-by-day schedule
  - Import to Google Calendar format

- [ ] Backend export endpoints
  - GET `/api/study-plans/{id}/export/pdf`
  - GET `/api/study-plans/{id}/export/csv`

### Beklenen Çıktı:
- `frontend/src/pages/StudyPlansListPage.tsx`
- PDF generation service
- CSV export function
- Export API endpoints

---

## 🎯 Implementation Strategy

### MVP Yaklaşımı (Recommended):
1. ✅ Phase 2.1.1 (Database) - TAMAMLANDI
2. ✅ Phase 2.1.2 (API) - TAMAMLANDI
3. ✅ Phase 2.1.3 (Wizard) - TAMAMLANDI
4. ✅ Phase 2.1.4 (Calendar View) - TAMAMLANDI
5. ✅ Phase 2.1.5 (Progress Tracking - Dashboard Integration) - TAMAMLANDI
6. ⏳ Phase 2.1.6 (Management & Export - OPTIONAL)

**🎉 STUDY PLAN GENERATOR TAM FONKSİYONEL!**
**Tüm temel özellikler tamamlandı. Phase 2.1.6 opsiyonel ek özellikler içerir.**

### Tam Özellik Yaklaşımı:
Sırayla tüm phase'leri tamamla: 2.1.1 → 2.1.2 → 2.1.3 → 2.1.4 → 2.1.5 → 2.1.6

---

## 📊 Claude AI Integration Details

### Study Plan Generation Prompt:
```
You are an expert study planner. Given the following information:
- Student's weak subjects and topics (from recommendations)
- Available study time per day: {daily_hours} hours
- Time frame: {days} days
- Study style: {intensive/balanced/relaxed}

Create a personalized study schedule that:
1. Prioritizes topics by impact score
2. Balances subjects across the week
3. Includes review sessions (20% of time)
4. Considers study style for daily load
5. Leaves rest days for balanced/relaxed styles

Output Format: JSON array of daily schedules
[
  {
    "day": 1,
    "date": "2025-01-15",
    "items": [
      {
        "recommendation_id": "...",
        "subject": "Matematik",
        "topic": "Permütasyon",
        "duration_minutes": 90,
        "order": 1
      }
    ]
  }
]
```

---

## 🔄 Data Flow

```
User Input (Wizard)
  ↓
Frontend State
  ↓
API: POST /api/study-plans/generate
  ↓
StudyPlanService.generate_study_plan()
  ↓
Claude AI (Smart Scheduling)
  ↓
Database (StudyPlan, StudyPlanDay, StudyPlanItem)
  ↓
API Response (JSON)
  ↓
Frontend Display (Calendar View)
  ↓
User Interaction (Check items)
  ↓
Progress Tracking & Updates
```

---

## 🎨 UI/UX Notes

### Color Coding by Subject:
- Matematik: Blue (#3b82f6)
- Fizik: Purple (#8b5cf6)
- Kimya: Green (#10b981)
- Biyoloji: Teal (#14b8a6)
- Türkçe: Red (#ef4444)
- Geometri: Orange (#f97316)

### Study Style Descriptions:
- **Yoğun**: 4+ saat/gün, minimal dinlenme, maksimum verimlilik
- **Dengeli**: 2-3 saat/gün, periyodik molalar, sürdürülebilir tempo
- **Rahat**: 1-2 saat/gün, bol tekrar, düşük stres

---

## ✅ Success Criteria

### Phase 2.1.1 Complete:
- [ ] 3 model oluşturuldu ve test edildi
- [ ] Migration çalıştı, database güncel
- [ ] İlişkiler doğru tanımlandı

### Phase 2.1.2 Complete:
- [ ] API endpoints çalışıyor
- [ ] Claude AI plan üretiyor
- [ ] Recommendations'dan plan oluşturuluyor

### Phase 2.1.3 Complete:
- [ ] 5 adımlı wizard tamamlandı
- [ ] Form validations çalışıyor
- [ ] Plan oluşturma başarılı

### Phase 2.1.4 Complete:
- [ ] Calendar view render ediliyor
- [ ] Günlük detaylar görüntüleniyor
- [ ] Progress gösterimi çalışıyor

### Phase 2.1.5 Complete:
- [ ] Item completion çalışıyor
- [ ] Progress hesaplaması doğru
- [ ] Dashboard widget eklendi

### Phase 2.1.6 Complete:
- [ ] PDF export çalışıyor
- [ ] CSV export çalışıyor
- [ ] Plan management özellikleri tamamlandı

---

**Başlangıç Tarihi:** 2025-10-27
**Planlanan Tamamlanma:** MVP için 1-2 gün

## 🚀 Next Step: Phase 2.1.1 - Database Models
