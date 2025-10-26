"""
Recommendation service for generating study suggestions
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import anthropic
import os

from app.models import Recommendation, Exam, ExamResult, SubjectResult, LearningOutcome, Student
from app.services.analytics_service import AnalyticsService


class RecommendationService:
    """Service for generating and managing study recommendations"""

    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)

    def generate_recommendations(self, student_id: str) -> List[Recommendation]:
        """
        Generate recommendations for a student based on their performance

        Steps:
        1. Detect patterns in student performance
        2. Calculate priority and impact scores
        3. Use Claude API to generate actionable suggestions
        4. Store recommendations in database
        """
        # Delete old active recommendations
        self.db.query(Recommendation).filter(
            Recommendation.student_id == student_id,
            Recommendation.is_active == True
        ).delete()
        self.db.commit()

        # Detect patterns
        patterns = self._detect_patterns(student_id)

        if not patterns:
            return []

        # Generate recommendations using Claude API
        recommendations = self._generate_ai_recommendations(student_id, patterns)

        # Store recommendations
        for rec_data in recommendations:
            recommendation = Recommendation(
                student_id=student_id,
                priority=rec_data["priority"],
                subject_name=rec_data.get("subject_name"),
                topic=rec_data.get("topic"),
                issue_type=rec_data["issue_type"],
                description=rec_data["description"],
                action_items=rec_data["action_items"],
                rationale=rec_data["rationale"],
                impact_score=rec_data["impact_score"],
                is_active=True
            )
            self.db.add(recommendation)

        self.db.commit()

        # Return fresh recommendations
        return self.db.query(Recommendation).filter(
            Recommendation.student_id == student_id,
            Recommendation.is_active == True
        ).order_by(Recommendation.priority).all()

    def _detect_patterns(self, student_id: str) -> List[Dict]:
        """
        Detect performance patterns that need attention

        Returns list of patterns like:
        - weak_subjects: Consistently low performing subjects
        - blank_patterns: High blank rate in certain topics
        - declining_trends: Subjects showing declining performance
        - weak_outcomes: Learning outcomes with low success rates
        """
        patterns = []

        # Get overview data
        overview = self.analytics_service.get_overview(student_id=student_id)

        if overview.stats.total_exams == 0:
            return patterns

        # Pattern 1: Weak subjects (average < 50%)
        weak_subjects = [s for s in overview.weak_subjects if s.average_percentage < 50]
        for subject in weak_subjects:
            patterns.append({
                "type": "weak_subject",
                "subject_name": subject.subject_name,
                "severity": "high" if subject.average_percentage < 30 else "medium",
                "data": {
                    "average_net": subject.average_net,
                    "average_percentage": subject.average_percentage,
                    "total_exams": subject.total_exams,
                    "trend": subject.improvement_trend
                }
            })

        # Pattern 2: Declining trends
        for subject in [*overview.top_subjects, *overview.weak_subjects]:
            if subject.improvement_trend == "declining":
                patterns.append({
                    "type": "declining_trend",
                    "subject_name": subject.subject_name,
                    "severity": "high",
                    "data": {
                        "average_net": subject.average_net,
                        "average_percentage": subject.average_percentage,
                        "total_exams": subject.total_exams
                    }
                })

        # Pattern 3: High blank rate (> 30% blank questions)
        for subject in [*overview.top_subjects, *overview.weak_subjects]:
            blank_rate = (subject.total_blank / subject.total_questions * 100) if subject.total_questions > 0 else 0
            if blank_rate > 30:
                patterns.append({
                    "type": "high_blank_rate",
                    "subject_name": subject.subject_name,
                    "severity": "medium",
                    "data": {
                        "blank_count": subject.total_blank,
                        "total_questions": subject.total_questions,
                        "blank_rate": blank_rate
                    }
                })

        # Pattern 4: Weak learning outcomes (success rate < 40%)
        all_outcomes = self.analytics_service.get_all_learning_outcomes(student_id=student_id)
        weak_outcomes = [o for o in all_outcomes if o.average_success_rate < 40]

        # Group by subject
        outcomes_by_subject = {}
        for outcome in weak_outcomes:
            if outcome.subject_name not in outcomes_by_subject:
                outcomes_by_subject[outcome.subject_name] = []
            outcomes_by_subject[outcome.subject_name].append(outcome)

        for subject_name, outcomes in outcomes_by_subject.items():
            if len(outcomes) >= 2:  # Only if multiple weak outcomes in same subject
                patterns.append({
                    "type": "weak_outcomes",
                    "subject_name": subject_name,
                    "severity": "high" if len(outcomes) >= 3 else "medium",
                    "data": {
                        "outcomes": [
                            {
                                "category": o.category,
                                "subcategory": o.subcategory,
                                "description": o.outcome_description,
                                "success_rate": o.average_success_rate
                            } for o in outcomes[:5]  # Limit to top 5
                        ]
                    }
                })

        return patterns

    def _generate_ai_recommendations(self, student_id: str, patterns: List[Dict]) -> List[Dict]:
        """
        Use Claude API to generate actionable study recommendations
        """
        if not patterns:
            return []

        # Get student info
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return []

        # Prepare context for Claude
        context = self._prepare_context_for_claude(student, patterns)

        # Call Claude API
        try:
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

            prompt = f"""Sen bir üniversite sınavı hazırlık danışmanısın. Aşağıdaki öğrenci performans verilerine dayanarak spesifik, uygulanabilir çalışma önerileri oluştur.

Öğrenci Bilgileri:
- İsim: {student.name}
- Okul: {student.school}
- Sınıf: {student.grade}
- Program: {student.program or 'Belirtilmemiş'}

Tespit Edilen Performans Sorunları:
{context}

Lütfen her sorun için şu formatta öneriler oluştur:

{{
  "priority": 1-5 arası sayı (1=en önemli),
  "subject_name": "Ders adı",
  "topic": "Spesifik konu/alan",
  "issue_type": "weak_subject/declining_trend/high_blank_rate/weak_outcomes",
  "description": "Sorunun kısa açıklaması (1-2 cümle)",
  "action_items": ["Somut aksiyon 1", "Somut aksiyon 2", "Somut aksiyon 3"],
  "rationale": "Neden bu öneri önemli (2-3 cümle)",
  "impact_score": 1-10 arası sayı (beklenen etki)
}}

Öneriler:
- Spesifik ve uygulanabilir olmalı
- Günlük/haftalık çalışma planı içermeli
- Kaynak önerileri (kitap, video, soru bankası vb.) içermeli
- Zaman yönetimi ipuçları içermeli
- En önemli 5-8 öneri üret
- JSON array formatında dön

SADECE JSON ARRAY DÖNDÜR, BAŞKA HİÇBİR ŞEY EKLEME."""

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = message.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            import json
            recommendations = json.loads(response_text)

            return recommendations

        except Exception as e:
            print(f"Error generating AI recommendations: {e}")
            # Fallback to simple recommendations based on patterns
            return self._generate_fallback_recommendations(patterns)

    def _prepare_context_for_claude(self, student: Student, patterns: List[Dict]) -> str:
        """Prepare human-readable context from patterns"""
        context_lines = []

        for i, pattern in enumerate(patterns, 1):
            pattern_type = pattern["type"]
            subject = pattern.get("subject_name", "Genel")
            severity = pattern["severity"]
            data = pattern["data"]

            if pattern_type == "weak_subject":
                context_lines.append(
                    f"{i}. {subject} - Zayıf Ders (Önem: {severity})\n"
                    f"   - Ortalama net: {data['average_net']:.2f}\n"
                    f"   - Başarı oranı: %{data['average_percentage']:.1f}\n"
                    f"   - Sınav sayısı: {data['total_exams']}\n"
                    f"   - Trend: {data['trend']}"
                )
            elif pattern_type == "declining_trend":
                context_lines.append(
                    f"{i}. {subject} - Düşüş Trendi (Önem: {severity})\n"
                    f"   - Ortalama net: {data['average_net']:.2f}\n"
                    f"   - Son sınavlarda düşüş gözlemlendi"
                )
            elif pattern_type == "high_blank_rate":
                context_lines.append(
                    f"{i}. {subject} - Yüksek Boş Bırakma (Önem: {severity})\n"
                    f"   - Boş soru: {data['blank_count']}/{data['total_questions']}\n"
                    f"   - Boş bırakma oranı: %{data['blank_rate']:.1f}"
                )
            elif pattern_type == "weak_outcomes":
                outcomes_text = "\n".join([
                    f"     * {o['category']} - {o.get('subcategory', '')} (Başarı: %{o['success_rate']:.1f})"
                    for o in data['outcomes'][:3]
                ])
                context_lines.append(
                    f"{i}. {subject} - Zayıf Kazanımlar (Önem: {severity})\n"
                    f"   - {len(data['outcomes'])} kazanımda düşük başarı\n"
                    f"   - Zayıf alanlar:\n{outcomes_text}"
                )

        return "\n\n".join(context_lines)

    def _generate_fallback_recommendations(self, patterns: List[Dict]) -> List[Dict]:
        """Generate simple recommendations if Claude API fails"""
        recommendations = []

        for pattern in patterns[:5]:  # Limit to 5
            priority = 1 if pattern["severity"] == "high" else 2
            subject = pattern.get("subject_name", "Genel")
            pattern_type = pattern["type"]

            if pattern_type == "weak_subject":
                recommendations.append({
                    "priority": priority,
                    "subject_name": subject,
                    "topic": "Genel Çalışma",
                    "issue_type": "weak_subject",
                    "description": f"{subject} dersinde ortalama başarı düşük",
                    "action_items": [
                        f"{subject} için günde en az 1 saat çalışma yapın",
                        "Temel konuları tekrar edin",
                        "Soru çözüm hızınızı artırın"
                    ],
                    "rationale": "Bu derste performansınızı artırmak genel netinizi önemli ölçüde yükseltecektir.",
                    "impact_score": 8.0
                })

        return recommendations

    def get_active_recommendations(self, student_id: str) -> List[Recommendation]:
        """Get active recommendations for a student"""
        return self.db.query(Recommendation).filter(
            Recommendation.student_id == student_id,
            Recommendation.is_active == True
        ).order_by(Recommendation.priority).all()

    def mark_as_completed(self, recommendation_id: str) -> bool:
        """Mark a recommendation as completed (inactive)"""
        rec = self.db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()

        if rec:
            rec.is_active = False
            self.db.commit()
            return True

        return False
