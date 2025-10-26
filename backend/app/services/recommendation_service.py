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
from app.core.config import settings


class RecommendationService:
    """Service for generating and managing study recommendations"""

    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)

    def generate_recommendations(self, student_id: str) -> Dict:
        """
        Intelligently generate/update recommendations based on student performance

        Steps:
        1. Detect patterns in student performance
        2. Get existing active recommendations
        3. Compare new patterns with existing recommendations
        4. Categorize as: new, updated, confirmed, resolved
        5. Use Claude API for new/updated recommendations only
        6. Update database intelligently

        Returns:
            Dict with 'recommendations' and 'summary' of changes
        """
        # Detect current patterns
        patterns = self._detect_patterns(student_id)

        # Get existing active recommendations
        existing_recs = self.db.query(Recommendation).filter(
            Recommendation.student_id == student_id,
            Recommendation.is_active == True
        ).all()

        # Compare patterns with existing recommendations
        comparison_result = self._compare_recommendations(patterns, existing_recs)

        # Generate AI recommendations for new and updated patterns only
        new_recs_data = []
        if comparison_result["new_patterns"] or comparison_result["updated_patterns"]:
            patterns_for_ai = comparison_result["new_patterns"] + comparison_result["updated_patterns"]
            new_recs_data = self._generate_ai_recommendations(student_id, patterns_for_ai)

        # Process each category
        new_count = 0
        updated_count = 0
        confirmed_count = 0
        resolved_count = 0

        # 1. Mark resolved recommendations (issues no longer present)
        for rec_id in comparison_result["resolved_rec_ids"]:
            rec = self.db.query(Recommendation).filter(Recommendation.id == rec_id).first()
            if rec:
                rec.status = 'resolved'
                rec.is_active = False
                resolved_count += 1

        # 2. Confirm still-valid recommendations (same pattern still exists)
        for rec_id in comparison_result["confirmed_rec_ids"]:
            rec = self.db.query(Recommendation).filter(Recommendation.id == rec_id).first()
            if rec:
                rec.status = 'active'
                rec.last_confirmed_at = datetime.utcnow()
                confirmed_count += 1

        # 3. Create new recommendations
        new_rec_ids_map = {}  # Map pattern to new recommendation
        for i, rec_data in enumerate(new_recs_data):
            pattern_idx = comparison_result.get("pattern_indices", {}).get(i)
            is_new = pattern_idx in [p["index"] for p in comparison_result["new_patterns"]]

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
                learning_outcome_ids=rec_data.get("learning_outcome_ids"),
                is_active=True,
                status='new' if is_new else 'updated',
                previous_recommendation_id=rec_data.get("previous_recommendation_id")
            )
            self.db.add(recommendation)

            if is_new:
                new_count += 1
            else:
                updated_count += 1
                # Mark old version as superseded
                if rec_data.get("previous_recommendation_id"):
                    old_rec = self.db.query(Recommendation).filter(
                        Recommendation.id == rec_data["previous_recommendation_id"]
                    ).first()
                    if old_rec:
                        old_rec.status = 'superseded'
                        old_rec.is_active = False

        self.db.commit()

        # Get all active recommendations
        active_recommendations = self.db.query(Recommendation).filter(
            Recommendation.student_id == student_id,
            Recommendation.is_active == True
        ).order_by(Recommendation.priority).all()

        return {
            "recommendations": active_recommendations,
            "summary": {
                "new_count": new_count,
                "updated_count": updated_count,
                "confirmed_count": confirmed_count,
                "resolved_count": resolved_count,
                "total_active": len(active_recommendations)
            }
        }

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

        # Pattern 4: Learning outcomes by status
        # Group outcomes by status: Zayıf (<40%), Orta (40-60%), İyi (60-80%), Çok İyi (≥80%)
        all_outcomes = self.analytics_service.get_all_learning_outcomes(student_id=student_id)

        # Categorize by success rate
        weak_outcomes = []  # Zayıf: <40%
        medium_outcomes = []  # Orta: 40-60%
        good_outcomes = []  # İyi: 60-80%

        for o in all_outcomes:
            rate = o.average_success_rate
            if rate < 40:
                weak_outcomes.append(o)
            elif rate < 60:
                medium_outcomes.append(o)
            elif rate < 80:
                good_outcomes.append(o)

        # Focus on weak and medium outcomes (need improvement)
        priority_outcomes = weak_outcomes + medium_outcomes

        # Group by subject
        outcomes_by_subject = {}
        for outcome in priority_outcomes:
            if outcome.subject_name not in outcomes_by_subject:
                outcomes_by_subject[outcome.subject_name] = []
            outcomes_by_subject[outcome.subject_name].append(outcome)

        # Get actual LearningOutcome objects for IDs
        outcome_query = self.db.query(LearningOutcome).join(Exam).filter(
            Exam.student_id == student_id
        ).all()

        # Create a mapping for finding IDs
        outcome_id_map = {}
        for lo in outcome_query:
            key = (lo.subject_name, lo.category or "", lo.subcategory or "", lo.outcome_description or "")
            if key not in outcome_id_map:
                outcome_id_map[key] = []
            outcome_id_map[key].append(lo.id)

        for subject_name, outcomes in outcomes_by_subject.items():
            if len(outcomes) >= 2:  # Only if multiple outcomes need improvement
                # Determine severity based on weak outcomes count
                weak_count = sum(1 for o in outcomes if o.average_success_rate < 40)
                severity = "high" if weak_count >= 3 else ("medium" if weak_count >= 1 else "low")

                outcome_details = []
                outcome_ids = []

                for o in outcomes[:5]:  # Limit to top 5
                    # Find IDs for this outcome
                    key = (o.subject_name, o.category or "", o.subcategory or "", o.outcome_description or "")
                    ids = outcome_id_map.get(key, [])
                    outcome_ids.extend(ids)

                    outcome_details.append({
                        "category": o.category,
                        "subcategory": o.subcategory,
                        "description": o.outcome_description,
                        "success_rate": o.average_success_rate,
                        "status": "zayıf" if o.average_success_rate < 40 else "orta"
                    })

                patterns.append({
                    "type": "weak_outcomes",
                    "subject_name": subject_name,
                    "severity": severity,
                    "data": {
                        "outcomes": outcome_details,
                        "outcome_ids": list(set(outcome_ids))  # Unique IDs
                    }
                })

        return patterns

    def _compare_recommendations(
        self,
        patterns: List[Dict],
        existing_recs: List[Recommendation]
    ) -> Dict:
        """
        Compare new patterns with existing recommendations to categorize changes

        Returns:
            {
                "new_patterns": [patterns with no matching recommendation],
                "updated_patterns": [patterns with changed data],
                "confirmed_rec_ids": [recommendation IDs still valid],
                "resolved_rec_ids": [recommendation IDs no longer needed],
                "pattern_indices": {new_rec_index: pattern_index} for tracking
            }
        """
        new_patterns = []
        updated_patterns = []
        confirmed_rec_ids = []
        resolved_rec_ids = []
        matched_rec_ids = set()

        # Add index to patterns for tracking
        for idx, pattern in enumerate(patterns):
            pattern["index"] = idx

        # For each pattern, find if there's a matching existing recommendation
        for pattern in patterns:
            match_found = False
            best_match = None
            best_match_score = 0

            for rec in existing_recs:
                # Check if pattern matches recommendation
                # Match criteria: same subject + same issue_type
                if (rec.subject_name == pattern.get("subject_name") and
                    rec.issue_type == pattern["type"]):

                    score = 1.0  # Base match

                    # Check if data significantly changed (needs update)
                    data_changed = self._check_if_data_changed(pattern, rec)

                    if data_changed:
                        score = 0.5  # Partial match (needs update)

                    if score > best_match_score:
                        best_match_score = score
                        best_match = rec
                        match_found = True

            if match_found and best_match:
                matched_rec_ids.add(best_match.id)

                if best_match_score >= 1.0:
                    # Exact match - confirm existing recommendation
                    confirmed_rec_ids.append(best_match.id)
                else:
                    # Partial match - data changed, needs update
                    pattern["previous_recommendation_id"] = best_match.id
                    updated_patterns.append(pattern)
            else:
                # No match - new recommendation needed
                new_patterns.append(pattern)

        # Find resolved recommendations (no matching pattern)
        for rec in existing_recs:
            if rec.id not in matched_rec_ids:
                resolved_rec_ids.append(rec.id)

        return {
            "new_patterns": new_patterns,
            "updated_patterns": updated_patterns,
            "confirmed_rec_ids": confirmed_rec_ids,
            "resolved_rec_ids": resolved_rec_ids,
            "pattern_indices": {i: p["index"] for i, p in enumerate(new_patterns + updated_patterns)}
        }

    def _check_if_data_changed(self, pattern: Dict, rec: Recommendation) -> bool:
        """
        Check if pattern data has significantly changed compared to recommendation

        Returns True if update is needed
        """
        pattern_type = pattern["type"]
        data = pattern["data"]

        # For weak_outcomes, check if success rates changed significantly (>5%)
        if pattern_type == "weak_outcomes":
            # We can't easily compare without storing original data
            # For now, assume it changed if the pattern still exists
            return False

        # For weak_subject, check if percentage changed significantly
        if pattern_type == "weak_subject":
            # Would need to parse stored description or rationale
            # For simplicity, assume significant change if severity changed
            return True  # Conservative - always update

        # For other types, consider changed
        return False

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
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

            prompt = f"""Sen bir üniversite sınavı hazırlık danışmanısın. Aşağıdaki öğrenci performans verilerine dayanarak spesifik, uygulanabilir çalışma önerileri oluştur.

Öğrenci Bilgileri:
- İsim: {student.name}
- Okul: {student.school}
- Sınıf: {student.grade}
- Program: {student.program or 'Belirtilmemiş'}

Tespit Edilen Performans Sorunları:
{context}

Lütfen her sorun için şu formatta öneriler oluştur. ÖNEMLİ: Zayıf kazanımlar için kategori ve alt kategori bilgilerini kullanarak çok spesifik konu önerileri yap:

{{
  "priority": 1-5 arası sayı (1=en önemli),
  "subject_name": "Ders adı",
  "topic": "Spesifik konu/alan (kazanım varsa category-subcategory kullan)",
  "issue_type": "weak_subject/declining_trend/high_blank_rate/weak_outcomes",
  "description": "Sorunun kısa açıklaması (1-2 cümle)",
  "action_items": ["Somut aksiyon 1", "Somut aksiyon 2", "Somut aksiyon 3"],
  "rationale": "Neden bu öneri önemli (2-3 cümle)",
  "impact_score": 1-10 arası sayı (beklenen etki),
  "learning_outcome_ids": null  // Bu alan backend tarafından doldurulacak
}}

Öneriler:
- Kazanım bazlı öneriler için category ve subcategory bilgilerini topic alanında kullan (örn: "Sayılar ve Cebir - Denklemler")
- Spesifik ve uygulanabilir olmalı
- Günlük/haftalık çalışma planı içermeli
- Kaynak önerileri (kitap, video, soru bankası, konu anlatımı vb.) içermeli
- Zaman yönetimi ipuçları içermeli
- En önemli 5-8 öneri üret
- JSON array formatında dön

SADECE JSON ARRAY DÖNDÜR, BAŞKA HİÇBİR ŞEY EKLEME."""

            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
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

            # Enrich recommendations with pattern data (learning_outcome_ids, previous_recommendation_id)
            for i, rec in enumerate(recommendations):
                if i < len(patterns):
                    pattern = patterns[i]

                    # Add learning outcome IDs if this is a weak_outcomes pattern
                    if pattern["type"] == "weak_outcomes" and "outcome_ids" in pattern.get("data", {}):
                        rec["learning_outcome_ids"] = pattern["data"]["outcome_ids"]

                    # Add previous recommendation ID if this is an update
                    if "previous_recommendation_id" in pattern:
                        rec["previous_recommendation_id"] = pattern["previous_recommendation_id"]

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
                    f"     * [{o['status'].upper()}] {o['category']}" +
                    (f" / {o.get('subcategory', '')}" if o.get('subcategory') else "") +
                    (f"\n       Kazanım: {o.get('description', '')}" if o.get('description') else "") +
                    f"\n       Başarı: %{o['success_rate']:.1f}"
                    for o in data['outcomes'][:5]
                ])
                context_lines.append(
                    f"{i}. {subject} - Zayıf Kazanımlar (Önem: {severity})\n"
                    f"   - {len(data['outcomes'])} kazanımda düşük başarı\n"
                    f"   - Detaylı kazanım analizi:\n{outcomes_text}"
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
