#!/usr/bin/env python3
"""
End-to-End test for the complete resource curation system (Phase 5)
Tests the full algorithm from study plan item to resource recommendations
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.resource_service import ResourceService
from app.models import StudyPlanItem, StudyPlanDay
import uuid
from datetime import datetime, timedelta


def test_end_to_end_curation():
    """Test the complete resource curation pipeline"""

    print("\n" + "="*70)
    print("END-TO-END RESOURCE CURATION TEST")
    print("="*70)

    db = SessionLocal()

    try:
        # Create a test study plan day first
        print("\n1️⃣ Creating test study plan day and item...")
        test_day = StudyPlanDay(
            id=str(uuid.uuid4()),
            date=datetime.utcnow().date() + timedelta(days=1),
            total_duration_minutes=60,
            notes="Test day for resource curation"
        )
        db.add(test_day)
        db.flush()  # Get the day ID

        # Create test study plan item
        test_item = StudyPlanItem(
            id=str(uuid.uuid4()),
            day_id=test_day.id,
            subject_name="Fizik",
            topic="Optik ve Işık",
            description="Işığın kırılması, yansıması ve prizmalar",
            duration_minutes=60,
            order=1,
            completed=False
        )

        db.add(test_item)
        db.commit()
        print(f"   ✅ Created: {test_item.subject_name} - {test_item.topic}")
        print(f"   ID: {test_item.id}")

        # Test resource curation
        print("\n2️⃣ Starting resource curation...")
        print("="*70)

        service = ResourceService(db)
        resources = service.curate_resources_for_study_item(
            study_plan_item_id=test_item.id
        )

        print("="*70)
        print("\n3️⃣ RESULTS:")
        print("="*70)

        youtube_resources = resources.get('youtube', [])
        print(f"\n📺 YouTube Resources: {len(youtube_resources)} found")

        if youtube_resources:
            print("\nTop 5 Recommended Videos:")
            for i, resource in enumerate(youtube_resources[:5], 1):
                print(f"\n{i}. {resource.name}")
                print(f"   URL: {resource.url}")
                print(f"   Channel: {resource.extra_data.get('channel_name_db', 'N/A')}")
                print(f"   Quality Score: {resource.quality_score:.1f}/100")
                print(f"   Views: {resource.extra_data.get('view_count', 0):,}")
                print(f"   Likes: {resource.extra_data.get('like_count', 0):,}")
                print(f"   Like Ratio: {resource.extra_data.get('like_ratio', 0):.2f}%")
                print(f"   Comments: {resource.extra_data.get('comment_count', 0):,}")
                print(f"   Duration: {resource.extra_data.get('duration_seconds', 0) // 60} min")
                print(f"   Channel Trust: {resource.extra_data.get('channel_trust_score', 0):.0f}/100")
        else:
            print("   ⚠️ No videos found (filters might be too strict for this topic)")

        # Summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"Subject: {test_item.subject_name}")
        print(f"Topic: {test_item.topic}")
        print(f"Resources Found: {len(youtube_resources)}")

        if youtube_resources:
            avg_score = sum(r.quality_score for r in youtube_resources) / len(youtube_resources)
            print(f"Average Quality Score: {avg_score:.1f}/100")

            avg_views = sum(r.extra_data.get('view_count', 0) for r in youtube_resources) / len(youtube_resources)
            print(f"Average Views: {avg_views:,.0f}")

            avg_like_ratio = sum(r.extra_data.get('like_ratio', 0) for r in youtube_resources) / len(youtube_resources)
            print(f"Average Like Ratio: {avg_like_ratio:.2f}%")

        print("\n✅ END-TO-END TEST COMPLETED!")
        print("="*70)

        # Cleanup
        print("\n4️⃣ Cleaning up test data...")
        for resource in youtube_resources:
            db.delete(resource)
        db.delete(test_item)
        db.delete(test_day)
        db.commit()
        print("   ✅ Test data cleaned up")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    test_end_to_end_curation()
