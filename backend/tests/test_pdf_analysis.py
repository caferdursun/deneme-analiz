"""
Test PDF analysis directly with retry mechanism
"""
import sys
sys.path.insert(0, '/root/projects/deneme-analiz/backend')

from app.utils.claude_client import ClaudeClient

pdf_path = '/root/projects/deneme-analiz/backend/data/e5a94f6f-8b83-437b-9e4d-25729212626c.pdf'

print(f"Testing PDF analysis: {pdf_path}")
print("=" * 80)

try:
    client = ClaudeClient()
    print("✓ Claude client initialized")

    print("\nStarting 5-stage extraction...")
    result = client.analyze_exam_pdf_staged(pdf_path)

    print("\n✅ SUCCESS!")
    print(f"Student: {result['student']['name']}")
    print(f"Exam: {result['exam']['exam_name']}")
    print(f"Subjects: {len(result['subjects'])}")
    print(f"Learning outcomes: {len(result['learning_outcomes'])}")
    print(f"Questions: {len(result['questions'])}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
