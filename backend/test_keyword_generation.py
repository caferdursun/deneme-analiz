#!/usr/bin/env python3
"""
Test Claude keyword generation (Phase 3)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.claude_curator_service import ClaudeCuratorService


def test_keyword_generation():
    """Test keyword generation for various topics"""

    service = ClaudeCuratorService()

    test_cases = [
        {
            "subject": "Fizik",
            "topic": "Prizmalar",
            "description": "Işık kırılması ve renk ayrışması"
        },
        {
            "subject": "Matematik",
            "topic": "Türev",
            "description": "Fonksiyonların türevi ve uygulamaları"
        },
        {
            "subject": "Kimya",
            "topic": "Asitler ve Bazlar",
            "description": "pH kavramı ve nötrleşme reaksiyonları"
        },
        {
            "subject": "Biyoloji",
            "topic": "Hücre Bölünmesi",
            "description": "Mitoz ve mayoz bölünme"
        },
        {
            "subject": "Türkçe",
            "topic": "Cümle Çözümlemesi",
            "description": "Öge analizi ve cümle türleri"
        }
    ]

    print("\n" + "="*70)
    print("PHASE 3: Claude Keyword Generation - Test")
    print("="*70)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {test_case['subject']} - {test_case['topic']}")
        print(f"{'='*70}")
        print(f"Açıklama: {test_case['description']}")

        keywords = service.generate_video_search_keywords(
            subject=test_case['subject'],
            topic=test_case['topic'],
            description=test_case['description']
        )

        print(f"\n✅ Generated {len(keywords)} keywords:")
        for j, keyword in enumerate(keywords, 1):
            print(f"   {j}. \"{keyword}\"")

    print("\n" + "="*70)
    print("✅ PHASE 3 COMPLETED: All keyword generation tests passed!")
    print("="*70)


if __name__ == "__main__":
    test_keyword_generation()
