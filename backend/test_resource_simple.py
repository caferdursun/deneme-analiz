#!/usr/bin/env python3
"""
Simple test for resource curation - bypasses StudyPlanItem complexity
Tests the core algorithm directly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.channel_service import ChannelService
from app.services.claude_curator_service import ClaudeCuratorService
from app.services.youtube_service import YouTubeService


def test_simple_resource_curation():
    """Test the core curation algorithm without database complexity"""

    print("\n" + "="*70)
    print("SIMPLE RESOURCE CURATION TEST")
    print("="*70)

    # Test parameters
    subject = "Fizik"
    topic = "Optik ve Işık"
    description = "Işığın kırılması, yansıması ve prizmalar"

    db = SessionLocal()

    try:
        # 1. Get channels
        print(f"\n1️⃣ Finding channels for {subject}...")
        channel_service = ChannelService(db)
        channels = channel_service.get_trusted_channels(subject, limit=3)
        print(f"   ✅ Found {len(channels)} channels")
        for ch in channels:
            print(f"      - {ch.channel_name} ({ch.subscriber_count:,} subs)")

        # 2. Generate keywords
        print(f"\n2️⃣ Generating keywords for '{topic}'...")
        claude_service = ClaudeCuratorService()
        keywords = claude_service.generate_video_search_keywords(
            subject=subject,
            topic=topic,
            description=description
        )
        print(f"   ✅ Generated {len(keywords)} keywords:")
        for kw in keywords:
            print(f"      - \"{kw}\"")

        # 3. Search videos
        print(f"\n3️⃣ Searching videos...")
        youtube_service = YouTubeService()
        all_videos = []

        for channel in channels[:2]:  # Top 2 channels
            print(f"\n   📺 {channel.channel_name}:")
            for keyword in keywords[:2]:  # First 2 keywords
                videos = youtube_service.search_videos_in_channel(
                    channel_id=channel.channel_id,
                    query=keyword,
                    max_results=2
                )
                if videos:
                    print(f"      '{keyword}': {len(videos)} videos")
                    all_videos.extend(videos)

        # 4. Results
        print(f"\n4️⃣ Results:")
        print(f"   Total videos found: {len(all_videos)}")

        if all_videos:
            print(f"\n   Top 3 Videos:")
            for i, video in enumerate(all_videos[:3], 1):
                print(f"\n   {i}. {video['title'][:60]}...")
                print(f"      Channel: {video['channel_name']}")
                print(f"      Views: {video['view_count']:,}")
                print(f"      Likes: {video['like_count']:,} ({video['like_ratio']:.2f}%)")
                print(f"      Comments: {video['comment_count']:,}")
                print(f"      Duration: {video['duration_seconds'] // 60} min")
                print(f"      URL: {video['url']}")

        print("\n" + "="*70)
        print("✅ SIMPLE TEST COMPLETED!")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    test_simple_resource_curation()
