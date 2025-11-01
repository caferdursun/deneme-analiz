"""
Match learning outcomes to curriculum topics using Claude API
Optimized for minimal API calls and tokens
"""
import json
import os
from pathlib import Path
from anthropic import Anthropic
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import re
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Database connection
DATABASE_URL = "sqlite:///./deneme_analiz.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Claude API client
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
    print("💡 Please set it: export ANTHROPIC_API_KEY='your-key-here'")
    exit(1)

client = Anthropic(api_key=api_key)

def load_curriculum():
    """Load curriculum data from database"""
    query = """
    SELECT
        cs.subject_name,
        cg.grade,
        cu.unit_name,
        ct.id as topic_id,
        ct.topic_name
    FROM curriculum_subjects cs
    JOIN curriculum_grades cg ON cs.id = cg.subject_id
    JOIN curriculum_units cu ON cg.id = cu.grade_id
    JOIN curriculum_topics ct ON cu.id = ct.unit_id
    ORDER BY cs."order", cg.grade, cu.unit_no, ct."order"
    """
    result = session.execute(text(query))

    # Organize by subject and grade
    curriculum = defaultdict(list)
    for row in result:
        key = (row.subject_name, row.grade)
        curriculum[key].append({
            'topic_id': row.topic_id,
            'unit_name': row.unit_name,
            'topic_name': row.topic_name
        })

    return curriculum

def load_learning_outcomes():
    """Load learning outcomes from database"""
    query = """
    SELECT DISTINCT
        id,
        subject_name,
        category,
        subcategory
    FROM learning_outcomes
    WHERE is_merged = 0
    ORDER BY subject_name, category, subcategory
    """
    result = session.execute(text(query))

    outcomes = []
    for row in result:
        outcomes.append({
            'id': row.id,
            'subject_name': row.subject_name,
            'category': row.category,
            'subcategory': row.subcategory
        })

    return outcomes

def normalize_subject_name(subject_name):
    """
    Normalize subject name and extract grade
    Examples:
        "Matematik.09" → ("Matematik", "9")
        "Fizik.10" → ("Fizik", "10")
        "12. SINIF KURS EDEBİYAT YKS" → ("Türk Dili ve Edebiyatı", "12")
    """
    # Manual mappings for special cases
    manual_mappings = {
        "12. SINIF KURS EDEBİYAT YKS": ("Türk Dili ve Edebiyatı", "12"),
        "KURS 11-12. SINIF MATEMATİK": ("Matematik", "11"),
    }

    if subject_name in manual_mappings:
        return manual_mappings[subject_name]

    # Try pattern: "Subject.Grade"
    match = re.match(r"(.+?)\.(\d+)", subject_name)
    if match:
        subject = match.group(1)
        grade = match.group(2)
        return (subject, grade)

    # Try pattern: "Subject.Grade" with full grade
    match = re.match(r"(.+?)\.(\d{2})", subject_name)
    if match:
        subject = match.group(1)
        grade = match.group(2).lstrip('0')  # "09" → "9"
        return (subject, grade)

    return (subject_name, None)

def batch_outcomes_by_subject(outcomes):
    """Group outcomes by normalized subject+grade for batch processing"""
    batches = defaultdict(list)

    for outcome in outcomes:
        subject, grade = normalize_subject_name(outcome['subject_name'])
        key = (subject, grade)
        batches[key].append(outcome)

    return batches

def create_matching_prompt(outcomes_batch, curriculum_topics):
    """
    Create optimized prompt for Claude to match multiple outcomes at once
    This minimizes API calls by processing multiple outcomes in one request
    """
    # Prepare curriculum topics list (compact format)
    topics_text = ""
    for i, topic in enumerate(curriculum_topics, 1):
        topics_text += f"{i}. {topic['unit_name']} → {topic['topic_name']}\n"

    # Prepare outcomes list
    outcomes_text = ""
    for i, outcome in enumerate(outcomes_batch, 1):
        cat = outcome['category'] or "N/A"
        subcat = outcome['subcategory'] or "N/A"
        outcomes_text += f"{i}. Category: {cat} | Subcategory: {subcat}\n"

    prompt = f"""Sen bir eğitim müfredatı uzmanısın. Görevin, sınav kazanımlarını (learning outcomes) müfredat konularıyla eşleştirmek.

MÜFREDAT KONULARI:
{topics_text}

KAZANIMLAR:
{outcomes_text}

GÖREV:
Her kazanım için en uygun müfredat konusunu bul ve eşleştirme skorunu hesapla.

CEVAP FORMATI (JSON):
{{
  "matches": [
    {{
      "outcome_index": 1,
      "best_match": {{
        "topic_index": 5,
        "confidence": 85,
        "reasoning": "Kısa açıklama"
      }},
      "alternatives": [
        {{"topic_index": 3, "confidence": 65}}
      ]
    }}
  ]
}}

KURALLAR:
- confidence: 0-100 arası skor
- 70+ → güçlü eşleşme
- 50-69 → orta güvenlik
- <50 → zayıf eşleşme
- En fazla 2 alternatif öner
- reasoning: maksimum 15 kelime

Sadece JSON döndür, başka açıklama yapma."""

    return prompt

def match_batch_with_claude(outcomes_batch, curriculum_topics):
    """
    Send batch of outcomes to Claude for matching
    Returns mapping of outcome_id → topic_id with confidence scores
    """
    if not outcomes_batch or not curriculum_topics:
        return []

    prompt = create_matching_prompt(outcomes_batch, curriculum_topics)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse JSON response
        response_text = response.content[0].text.strip()

        # Try to extract JSON from markdown code blocks
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()

        result = json.loads(response_text)

        # Map results back to IDs
        matches = []
        for match in result.get('matches', []):
            outcome_idx = match['outcome_index'] - 1  # 0-indexed
            if outcome_idx >= len(outcomes_batch):
                continue

            outcome = outcomes_batch[outcome_idx]
            best = match.get('best_match', {})

            topic_idx = best.get('topic_index', 0) - 1  # 0-indexed
            if topic_idx < 0 or topic_idx >= len(curriculum_topics):
                continue

            topic = curriculum_topics[topic_idx]

            matches.append({
                'outcome_id': outcome['id'],
                'outcome_category': outcome['category'],
                'outcome_subcategory': outcome['subcategory'],
                'topic_id': topic['topic_id'],
                'topic_unit': topic['unit_name'],
                'topic_name': topic['topic_name'],
                'confidence': best.get('confidence', 0),
                'reasoning': best.get('reasoning', ''),
                'alternatives': match.get('alternatives', [])
            })

        return matches

    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {str(e)}")
        print(f"📄 Response preview: {response_text[:200]}...")
        return []
    except Exception as e:
        print(f"❌ Claude API error: {str(e)}")
        return []

def save_matches_to_json(all_matches, output_path):
    """Save matching results to JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_matches': len(all_matches),
            'matches': all_matches
        }, f, ensure_ascii=False, indent=2)

def main():
    print("🔄 Loading curriculum data...")
    curriculum = load_curriculum()

    print("🔄 Loading learning outcomes...")
    outcomes = load_learning_outcomes()

    print(f"📊 Total outcomes: {len(outcomes)}")
    print(f"📊 Curriculum subjects: {len(curriculum)} subject-grade combinations")

    print("\n🔄 Grouping outcomes by subject+grade for batch processing...")
    batches = batch_outcomes_by_subject(outcomes)

    print(f"📊 Created {len(batches)} batches")

    all_matches = []
    api_calls = 0

    for (subject, grade), outcomes_batch in batches.items():
        print(f"\n📌 Processing: {subject} Grade {grade} ({len(outcomes_batch)} outcomes)")

        # Get curriculum topics for this subject+grade
        curriculum_topics = curriculum.get((subject, grade), [])

        if not curriculum_topics:
            print(f"  ⚠️  No curriculum topics found for {subject} Grade {grade}")
            continue

        print(f"  📚 Found {len(curriculum_topics)} curriculum topics")

        # Process in sub-batches of max 10 outcomes per API call
        batch_size = 10
        for i in range(0, len(outcomes_batch), batch_size):
            sub_batch = outcomes_batch[i:i+batch_size]

            print(f"  🤖 Calling Claude API for outcomes {i+1}-{i+len(sub_batch)}...")
            matches = match_batch_with_claude(sub_batch, curriculum_topics)

            api_calls += 1
            all_matches.extend(matches)

            print(f"  ✅ Matched {len(matches)} outcomes")

    print(f"\n{'='*60}")
    print(f"✅ MATCHING COMPLETE!")
    print(f"📊 Total API calls: {api_calls}")
    print(f"📊 Total matches: {len(all_matches)}")
    print(f"📊 Average matches per call: {len(all_matches)/api_calls:.1f}")

    # Calculate confidence statistics
    if all_matches:
        confidences = [m['confidence'] for m in all_matches]
        avg_confidence = sum(confidences) / len(confidences)
        high_conf = len([c for c in confidences if c >= 70])
        med_conf = len([c for c in confidences if 50 <= c < 70])
        low_conf = len([c for c in confidences if c < 50])

        print(f"\n📈 Confidence Distribution:")
        print(f"  🟢 High (70+): {high_conf} ({high_conf/len(all_matches)*100:.1f}%)")
        print(f"  🟡 Medium (50-69): {med_conf} ({med_conf/len(all_matches)*100:.1f}%)")
        print(f"  🔴 Low (<50): {low_conf} ({low_conf/len(all_matches)*100:.1f}%)")
        print(f"  📊 Average confidence: {avg_confidence:.1f}")

    # Save results
    output_path = os.path.join(os.path.dirname(__file__), '../../temp/outcome_curriculum_matches.json')
    output_path = os.path.abspath(output_path)

    print(f"\n💾 Saving results to {output_path}...")
    save_matches_to_json(all_matches, output_path)

    print("✅ Done!")

    session.close()

if __name__ == "__main__":
    main()
