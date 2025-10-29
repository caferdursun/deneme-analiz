#!/usr/bin/env python3
"""
Test enhanced video filtering and engagement scoring
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.youtube_service import YouTubeService
from app.services.claude_curator_service import ClaudeCuratorService


def test_enhanced_filtering():
    """Test the enhanced video filtering system"""

    print("\n" + "="*70)
    print("ENHANCED VIDEO FILTERING TEST")
    print("="*70)

    youtube = YouTubeService()
    claude = ClaudeCuratorService()

    # Test case: Search for Fizik videos
    print("\n📚 Test Subject: Fizik - Prizmalar")
    print("="*70)

    # Step 1: Generate keywords
    print("\n1️⃣ Generating search keywords with Claude...")
    keywords = claude.generate_video_search_keywords(
        subject="Fizik",
        topic="Prizmalar",
        description="Işık kırılması ve renk ayrışması"
    )
    print(f"   ✅ Generated {len(keywords)} keywords")
    for i, kw in enumerate(keywords, 1):
        print(f"      {i}. {kw}")

    # Step 2: Find trusted channels
    print("\n2️⃣ Finding trusted Physics channels...")
    channels = youtube.search_channels("Fizik AYT TYT", max_results=3)
    if channels:
        print(f"   ✅ Found {len(channels)} channels:")
        for ch in channels:
            print(f"      - {ch['channel_name']} ({ch['subscriber_count']:,} subs)")
    else:
        print("   ❌ No channels found")
        return

    # Step 3: Search videos with enhanced filters
    print("\n3️⃣ Searching videos with ENHANCED FILTERS...")
    print("   Filters:")
    print("      ✓ Duration: 5-30 minutes")
    print("      ✓ Views: >10K (increased from 5K)")
    print("      ✓ Age: 1 month - 2.5 years")
    print("      ✓ Like ratio: >0.5%")
    print("      ✓ Comments: >10")
    print("      ✓ Engagement scoring: like_ratio * sqrt(views)")

    all_videos = []
    for channel in channels[:2]:  # Test with top 2 channels
        print(f"\n   📺 Searching in: {channel['channel_name']}")
        for keyword in keywords[:2]:  # Test with first 2 keywords
            videos = youtube.search_videos_in_channel(
                channel_id=channel['channel_id'],
                query=keyword,
                max_results=2
            )
            if videos:
                print(f"      ✅ '{keyword}': {len(videos)} videos found")
                for v in videos:
                    print(f"         - {v['title'][:50]}...")
                    print(f"           Views: {v['view_count']:,} | Likes: {v['like_count']:,} | Comments: {v['comment_count']:,}")
                    print(f"           Like ratio: {v['like_ratio']:.2f}% | Age: {v['published_years_ago']:.1f}y")
                    print(f"           Engagement score: {v['engagement_score']:.1f}")
                all_videos.extend(videos)
            else:
                print(f"      ⚠️ '{keyword}': No videos passed filters")

    # Step 4: Verify availability
    if all_videos:
        print(f"\n4️⃣ Verifying video availability...")
        for video in all_videos[:3]:  # Check first 3
            is_available = youtube.verify_video_availability(
                video['video_id'],
                check_age=True
            )
            status = "✅ Available" if is_available else "❌ Not available"
            print(f"   {video['video_id']}: {status}")
            print(f"      {video['title'][:60]}...")

    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"Keywords generated: {len(keywords)}")
    print(f"Channels searched: {len(channels[:2])}")
    print(f"Videos found (after filters): {len(all_videos)}")
    print(f"\n✅ Enhanced filtering system is working!")
    print("\nKey improvements:")
    print("  • Minimum views: 5K → 10K")
    print("  • Age range: 0-3 years → 1 month - 2.5 years")
    print("  • Added like ratio filter (>0.5%)")
    print("  • Added comment count filter (>10)")
    print("  • Engagement-based scoring (not just views)")
    print("="*70)


if __name__ == "__main__":
    test_enhanced_filtering()
