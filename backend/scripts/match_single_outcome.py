#!/usr/bin/env python3
"""
Match Single Unmapped Outcome
Quick script to match the remaining unmapped outcome
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
import anthropic
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.core.database import SessionLocal
from app.models.learning_outcome import LearningOutcome
from app.models.topic import Topic
from app.models.subject import Subject
from app.models.exam_type import ExamType


def main():
    """Match single unmapped outcome"""
    db = SessionLocal()

    try:
        # Find unmapped outcome
        unmapped_id = "8a1d1801-5e50-4b13-aaee-f28c4c9e84a2"

        outcome = db.query(LearningOutcome).filter(
            LearningOutcome.id == unmapped_id
        ).first()

        if not outcome:
            print("Outcome not found!")
            return

        print(f"Outcome: {outcome.subject_name}")
        print(f"Category: {outcome.category}")
        print(f"Subcategory: {outcome.subcategory}")
        print(f"Description: {outcome.outcome_description}")

        # Get Matematik topics
        topics = (
            db.query(Topic)
            .join(Subject)
            .filter(Subject.name == "Matematik")
            .options(joinedload(Topic.subject))
            .all()
        )

        print(f"\nFound {len(topics)} Matematik topics")

        # Create Claude prompt
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        prompt = f"""Sen bir matematik müfredatı uzmanısın. Bu kazanımı en uygun matematik konusuna eşleştir.

**Kazanım:**
Ders: {outcome.subject_name}
Kategori: {outcome.category}
Alt Kategori: {outcome.subcategory}
Açıklama: {outcome.outcome_description or "N/A"}

**Mevcut Konular:**
"""
        for i, topic in enumerate(topics[:30], 1):  # First 30 topics
            prompt += f"{i}. {topic.name}\n"

        prompt += """

**Görev:** En uygun 1-3 konuyu seç ve güven skoru (0-100) ver.

**Çıktı Formatı (JSON):**
{
  "matches": [
    {"topic_name": "Konu Adı", "confidence": 95, "reasoning": "Neden eşleşiyor"}
  ]
}
"""

        print("\nCalling Claude API...")
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text
        print(f"\nResponse: {response_text[:200]}...")

        # Parse JSON
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        json_str = response_text[start_idx:end_idx]
        parsed = json.loads(json_str)

        matches = parsed.get("matches", [])
        print(f"\nFound {len(matches)} matches")

        # Find topic objects and save
        topic_lookup = {t.name: t for t in topics}
        saved_count = 0

        for i, match in enumerate(matches):
            topic_name = match["topic_name"]
            confidence = match["confidence"]
            reasoning = match.get("reasoning", "")

            topic = topic_lookup.get(topic_name)
            if not topic:
                print(f"WARNING: Topic '{topic_name}' not found")
                continue

            # Check if exists
            existing = db.execute(
                text("""
                SELECT id FROM learning_outcome_topic_mappings
                WHERE learning_outcome_id = :outcome_id AND topic_id = :topic_id
                """),
                {"outcome_id": outcome.id, "topic_id": topic.id}
            ).fetchone()

            if existing:
                print(f"Mapping already exists for {topic_name}")
                continue

            # Insert
            mapping_id = str(uuid.uuid4())
            now = datetime.now()
            is_primary = (i == 0)

            db.execute(
                text("""
                INSERT INTO learning_outcome_topic_mappings
                (id, learning_outcome_id, topic_id, confidence_score, is_primary, created_at, updated_at)
                VALUES (:id, :outcome_id, :topic_id, :confidence, :is_primary, :created_at, :updated_at)
                """),
                {
                    "id": mapping_id,
                    "outcome_id": outcome.id,
                    "topic_id": topic.id,
                    "confidence": confidence,
                    "is_primary": is_primary,
                    "created_at": now,
                    "updated_at": now
                }
            )

            print(f"✓ Saved: {topic_name} (confidence: {confidence})")
            saved_count += 1

        db.commit()
        print(f"\n✓ Saved {saved_count} new mappings")

        # Final stats
        total = db.execute(text("SELECT COUNT(*) FROM learning_outcome_topic_mappings")).fetchone()[0]
        unmapped = db.execute(text("""
            SELECT COUNT(*) FROM learning_outcomes lo
            WHERE NOT EXISTS (
                SELECT 1 FROM learning_outcome_topic_mappings m WHERE m.learning_outcome_id = lo.id
            )
        """)).fetchone()[0]

        print(f"\n=== FINAL STATS ===")
        print(f"Total mappings: {total}")
        print(f"Unmapped outcomes: {unmapped}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
