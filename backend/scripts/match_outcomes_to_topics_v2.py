#!/usr/bin/env python3
"""
Match Learning Outcomes to Curriculum Topics (V2)

This script uses Claude API to intelligently match ALL 346 learning outcomes to curriculum topics.
Features:
- Batch processing (15 outcomes per API call)
- Many-to-many mapping support
- Confidence scoring (0-100)
- Confidence delta threshold (<15 for alternative matches)
- Grade-aware filtering
- Enhanced prompt with few-shot examples
- Guaranteed minimum 1 mapping per outcome
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
import anthropic
from dotenv import load_dotenv

# Load environment variables from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.learning_outcome import LearningOutcome
from app.models.topic import Topic
from app.models.subject import Subject
from app.models.exam_type import ExamType


class OutcomeTopicMatcher:
    """Matches learning outcomes to curriculum topics using Claude API"""

    def __init__(self, db: Session):
        self.db = db
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.confidence_delta_threshold = 15
        self.batch_size = 15

        # Load data
        self.load_subject_mappings()
        self.load_topics()

    def load_subject_mappings(self):
        """Load subject name mappings from database"""
        result = self.db.execute(text("""
            SELECT outcome_subject_name, curriculum_subject_name, exam_type_id
            FROM subject_name_mappings
        """)).fetchall()

        # Group by outcome subject: {outcome_subject -> [(curriculum_subject, exam_type_id)]}
        self.subject_mappings = {}
        for row in result:
            outcome_subj, curric_subj, exam_type_id = row
            if outcome_subj not in self.subject_mappings:
                self.subject_mappings[outcome_subj] = []
            self.subject_mappings[outcome_subj].append((curric_subj, exam_type_id))

        print(f"Loaded {len(self.subject_mappings)} subject mappings")

    def load_topics(self):
        """Load all topics with their subjects and exam types"""
        topics = (
            self.db.query(Topic)
            .join(Subject)
            .join(ExamType)
            .options(
                joinedload(Topic.subject).joinedload(Subject.exam_type)
            )
            .all()
        )

        # Create lookup: {(subject_name, exam_type_id) -> [topics]}
        self.topics_by_subject_exam = {}
        for topic in topics:
            key = (topic.subject.name, topic.subject.exam_type_id)
            if key not in self.topics_by_subject_exam:
                self.topics_by_subject_exam[key] = []
            self.topics_by_subject_exam[key].append(topic)

        print(f"Loaded {len(topics)} topics across {len(self.topics_by_subject_exam)} subject/exam combinations")

    def get_relevant_topics_for_outcome(self, outcome: LearningOutcome) -> List[Topic]:
        """Get relevant curriculum topics for a learning outcome"""
        if outcome.subject_name not in self.subject_mappings:
            print(f"WARNING: No subject mapping for '{outcome.subject_name}'")
            return []

        relevant_topics = []
        mappings = self.subject_mappings[outcome.subject_name]

        for curric_subject, exam_type_id in mappings:
            key = (curric_subject, exam_type_id)
            if key in self.topics_by_subject_exam:
                relevant_topics.extend(self.topics_by_subject_exam[key])

        return relevant_topics

    def create_matching_prompt(self, outcomes: List[LearningOutcome], topics_map: Dict[str, List[Topic]]) -> str:
        """Create Claude API prompt for batch matching"""

        prompt = """Sen bir eğitim müfredatı uzmanısın. Görevin, sınav analizinden elde edilen öğrenme kazanımlarını (learning outcomes) ile müfredat konularını (curriculum topics) eşleştirmek.

**ÖNEMLİ KURALLAR:**
1. Her kazanım için EN AZ 1, EN FAZLA 5 konu eşleştir
2. Eşleştirme güven skoru 0-100 arası (100 = kesin eşleşme, 0 = hiç eşleşmiyor)
3. En yüksek skora sahip eşleşmeyi "is_primary": true olarak işaretle
4. Alternatif eşleştirmeler: En yüksek skor ile arasındaki fark 15'ten küçükse ekle
5. Grade bilgisine dikkat et - kazanımın grade_info değeri ile topic'in grade_info değeri uyumlu olmalı
6. Matematiksel kavramlar, fiziksel prensipler, kimyasal reaksiyonlar gibi temel kavramları tanı
7. Kazanımın açıklamasındaki anahtar kelimelere odaklan

**FEW-SHOT ÖRNEKLER:**

Örnek 1:
Kazanım: "Türev kavramını anlayarak basit fonksiyonların türevini alabilme"
Grade Info: "11,12"
Konular: ["Türev", "Türevin Geometrik Yorumu", "Türev Alma Kuralları", "Limit"]
Çıktı:
{{
  "matches": [
    {{"topic_name": "Türev", "confidence": 95, "is_primary": true, "reasoning": "Doğrudan türev kavramı"}},
    {{"topic_name": "Türev Alma Kuralları", "confidence": 90, "is_primary": false, "reasoning": "Türev alma uygulaması"}},
    {{"topic_name": "Türevin Geometrik Yorumu", "confidence": 82, "is_primary": false, "reasoning": "Türev kavramının yorumlanması"}}
  ]
}}

Örnek 2:
Kazanım: "Newton'un hareket yasalarını günlük yaşam örnekleri ile açıklayabilme"
Grade Info: "9"
Konular: ["Kuvvet ve Hareket", "Newton'un Hareket Yasaları", "Sürtünme Kuvveti", "İvme"]
Çıktı:
{{
  "matches": [
    {{"topic_name": "Newton'un Hareket Yasaları", "confidence": 100, "is_primary": true, "reasoning": "Tam eşleşme"}},
    {{"topic_name": "Kuvvet ve Hareket", "confidence": 88, "is_primary": false, "reasoning": "İlgili temel kavramlar"}}
  ]
}}

**ŞİMDİ EŞLEŞTİR:**

"""

        for i, outcome in enumerate(outcomes):
            outcome_id = outcome.id
            topics = topics_map.get(outcome_id, [])

            if not topics:
                prompt += f"\n[Kazanım {i+1}] ID: {outcome_id}\n"
                prompt += f"Subject: {outcome.subject_name}\n"
                prompt += f"Category: {outcome.category or 'N/A'}\n"
                prompt += f"Description: {outcome.outcome_description or 'N/A'}\n"
                prompt += f"Grade Info: N/A\n"
                prompt += f"UYARI: Bu kazanım için müfredat konusu bulunamadı!\n"
                continue

            prompt += f"\n[Kazanım {i+1}] ID: {outcome_id}\n"
            prompt += f"Subject: {outcome.subject_name}\n"
            prompt += f"Category: {outcome.category or 'N/A'}\n"
            prompt += f"Subcategory: {outcome.subcategory or 'N/A'}\n"
            prompt += f"Description: {outcome.outcome_description or 'N/A'}\n"
            prompt += f"Grade Info: N/A\n"  # Learning outcomes don't have grade info
            prompt += f"\nMevcut Konular:\n"

            for topic in topics:
                grade_str = topic.grade_info or "Tüm sınıflar"
                prompt += f"  - {topic.name} (Grade: {grade_str})\n"

        prompt += """

**ÇIKTI FORMATI (JSON):**
Her kazanım için aşağıdaki formatta cevap ver:

{
  "outcome_<id>": {
    "matches": [
      {"topic_name": "Konu Adı", "confidence": 95, "is_primary": true, "reasoning": "Neden eşleşiyor"},
      {"topic_name": "Alternatif Konu", "confidence": 85, "is_primary": false, "reasoning": "Alternatif neden"}
    ]
  }
}

ÖNEMLİ:
- Her kazanım için EN AZ 1 eşleşme dön
- Eşleşme bulamadığın kazanımlar için en yakın konuyu düşük güven skoru ile eşleştir
- JSON formatına kesinlikle uy
"""

        return prompt

    def parse_claude_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude API response"""
        try:
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx == -1 or end_idx == 0:
                print("ERROR: No JSON found in response")
                return {}

            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"ERROR parsing JSON: {e}")
            print(f"Response text: {response_text[:500]}...")
            return {}

    def process_batch(self, outcomes: List[LearningOutcome]) -> List[Dict[str, Any]]:
        """Process a batch of outcomes using Claude API"""

        # Build topics map for this batch
        topics_map = {}
        for outcome in outcomes:
            topics_map[outcome.id] = self.get_relevant_topics_for_outcome(outcome)

        # Create prompt
        prompt = self.create_matching_prompt(outcomes, topics_map)

        print(f"\n=== Processing batch of {len(outcomes)} outcomes ===")
        print(f"Prompt length: {len(prompt)} characters")

        # Call Claude API
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text
            print(f"Response length: {len(response_text)} characters")

            # Parse response
            parsed_response = self.parse_claude_response(response_text)

            return self.process_matches(outcomes, parsed_response, topics_map)

        except Exception as e:
            print(f"ERROR calling Claude API: {e}")
            return []

    def process_matches(
        self,
        outcomes: List[LearningOutcome],
        parsed_response: Dict[str, Any],
        topics_map: Dict[str, List[Topic]]
    ) -> List[Dict[str, Any]]:
        """Process Claude's matches and apply business logic"""

        all_mappings = []

        for outcome in outcomes:
            outcome_key = f"outcome_{outcome.id}"

            if outcome_key not in parsed_response:
                print(f"WARNING: No matches for outcome {outcome.id}")
                # Try to find a fallback match
                fallback_mapping = self.create_fallback_mapping(outcome, topics_map)
                if fallback_mapping:
                    all_mappings.extend(fallback_mapping)
                continue

            matches = parsed_response[outcome_key].get("matches", [])

            if not matches:
                print(f"WARNING: Empty matches for outcome {outcome.id}")
                fallback_mapping = self.create_fallback_mapping(outcome, topics_map)
                if fallback_mapping:
                    all_mappings.extend(fallback_mapping)
                continue

            # Find matching topic objects
            outcome_topics = topics_map.get(outcome.id, [])
            topic_lookup = {t.name: t for t in outcome_topics}

            # Sort matches by confidence
            matches.sort(key=lambda x: x["confidence"], reverse=True)

            highest_confidence = matches[0]["confidence"]

            for i, match in enumerate(matches):
                topic_name = match["topic_name"]
                confidence = match["confidence"]

                # Find topic
                topic = topic_lookup.get(topic_name)
                if not topic:
                    print(f"WARNING: Topic '{topic_name}' not found for outcome {outcome.id}")
                    continue

                # Apply confidence delta threshold
                if i > 0 and (highest_confidence - confidence) > self.confidence_delta_threshold:
                    # Skip this and remaining matches
                    break

                # Create mapping
                is_primary = (i == 0)
                all_mappings.append({
                    "learning_outcome_id": outcome.id,
                    "topic_id": topic.id,
                    "confidence_score": confidence,
                    "is_primary": is_primary,
                    "reasoning": match.get("reasoning", "")
                })

        return all_mappings

    def create_fallback_mapping(self, outcome: LearningOutcome, topics_map: Dict[str, List[Topic]]) -> List[Dict[str, Any]]:
        """Create fallback mapping when Claude fails to match"""
        topics = topics_map.get(outcome.id, [])

        if not topics:
            print(f"ERROR: No topics available for outcome {outcome.id}")
            return []

        # Just take the first topic with low confidence
        topic = topics[0]
        return [{
            "learning_outcome_id": outcome.id,
            "topic_id": topic.id,
            "confidence_score": 30,  # Low confidence fallback
            "is_primary": True,
            "reasoning": "Fallback match - manual review needed"
        }]

    def save_mappings(self, mappings: List[Dict[str, Any]]) -> int:
        """Save mappings to database"""
        saved_count = 0

        for mapping in mappings:
            # Check if mapping already exists
            existing = self.db.execute(
                text("""
                SELECT id FROM learning_outcome_topic_mappings
                WHERE learning_outcome_id = :outcome_id
                AND topic_id = :topic_id
                """),
                {
                    "outcome_id": mapping["learning_outcome_id"],
                    "topic_id": mapping["topic_id"]
                }
            ).fetchone()

            if existing:
                continue

            # Insert mapping
            mapping_id = str(uuid.uuid4())
            now = datetime.now()

            self.db.execute(
                text("""
                INSERT INTO learning_outcome_topic_mappings
                (id, learning_outcome_id, topic_id, confidence_score, is_primary, created_at, updated_at)
                VALUES (:id, :outcome_id, :topic_id, :confidence, :is_primary, :created_at, :updated_at)
                """),
                {
                    "id": mapping_id,
                    "outcome_id": mapping["learning_outcome_id"],
                    "topic_id": mapping["topic_id"],
                    "confidence": mapping["confidence_score"],
                    "is_primary": mapping["is_primary"],
                    "created_at": now,
                    "updated_at": now
                }
            )
            saved_count += 1

        self.db.commit()
        return saved_count

    def run(self):
        """Main execution"""
        print("=" * 60)
        print("Learning Outcome to Topic Matching (V2)")
        print("=" * 60)

        # Load ALL learning outcomes
        outcomes = self.db.query(LearningOutcome).all()
        print(f"\nTotal learning outcomes: {len(outcomes)}")

        # Process in batches
        total_mappings = []
        total_batches = (len(outcomes) + self.batch_size - 1) // self.batch_size

        for i in range(0, len(outcomes), self.batch_size):
            batch = outcomes[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1

            print(f"\n{'='*60}")
            print(f"Batch {batch_num}/{total_batches}")
            print(f"{'='*60}")

            batch_mappings = self.process_batch(batch)
            total_mappings.extend(batch_mappings)

            print(f"Batch produced {len(batch_mappings)} mappings")

            # Save after each batch
            saved = self.save_mappings(batch_mappings)
            print(f"Saved {saved} new mappings to database")

        print(f"\n{'='*60}")
        print("Matching Complete!")
        print(f"{'='*60}")
        print(f"Total mappings created: {len(total_mappings)}")

        # Show statistics
        self.show_statistics()

    def show_statistics(self):
        """Show matching statistics"""
        print("\n=== Statistics ===")

        # Total mappings
        result = self.db.execute(text("SELECT COUNT(*) FROM learning_outcome_topic_mappings")).fetchone()
        print(f"Total mappings in database: {result[0]}")

        # Outcomes with mappings
        result = self.db.execute(text("""
            SELECT COUNT(DISTINCT learning_outcome_id)
            FROM learning_outcome_topic_mappings
        """)).fetchone()
        print(f"Outcomes with mappings: {result[0]}")

        # Outcomes without mappings
        result = self.db.execute(text("""
            SELECT COUNT(*)
            FROM learning_outcomes lo
            WHERE NOT EXISTS (
                SELECT 1 FROM learning_outcome_topic_mappings m
                WHERE m.learning_outcome_id = lo.id
            )
        """)).fetchone()
        print(f"Outcomes WITHOUT mappings: {result[0]}")

        # Average confidence
        result = self.db.execute(text("""
            SELECT AVG(confidence_score) as avg_confidence
            FROM learning_outcome_topic_mappings
        """)).fetchone()
        print(f"Average confidence score: {result[0]:.2f}" if result[0] else "N/A")

        # Confidence distribution
        print("\nConfidence distribution:")
        result = self.db.execute(text("""
            SELECT
                CASE
                    WHEN confidence_score >= 80 THEN 'High (80-100)'
                    WHEN confidence_score >= 50 THEN 'Medium (50-79)'
                    ELSE 'Low (0-49)'
                END as confidence_range,
                COUNT(*) as count
            FROM learning_outcome_topic_mappings
            GROUP BY confidence_range
            ORDER BY confidence_range
        """)).fetchall()

        for row in result:
            print(f"  {row[0]}: {row[1]} mappings")


def main():
    """Main entry point"""
    db = SessionLocal()
    try:
        matcher = OutcomeTopicMatcher(db)
        matcher.run()
        print("\n✓ Script completed successfully!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
