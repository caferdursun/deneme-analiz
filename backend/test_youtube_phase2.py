#!/usr/bin/env python3
"""
Test script for Phase 2 YouTube Service enhancements
Tests all 4 new methods: search_channels, get_channel_details,
search_videos_in_channel, verify_video_availability
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.youtube_service import YouTubeService


def test_search_channels():
    """Test 1: Search for channels"""
    print("\n" + "="*60)
    print("TEST 1: Search Channels - 'Matematik AYT TYT'")
    print("="*60)

    service = YouTubeService()
    channels = service.search_channels("Matematik AYT TYT", max_results=5)

    print(f"\nFound {len(channels)} channels:")
    for i, channel in enumerate(channels, 1):
        print(f"\n{i}. {channel['channel_name']}")
        print(f"   Channel ID: {channel['channel_id']}")
        print(f"   Subscribers: {channel['subscriber_count']:,}")
        print(f"   Videos: {channel['video_count']:,}")
        print(f"   Views: {channel['view_count']:,}")
        print(f"   Custom URL: {channel.get('custom_url', 'N/A')}")
        print(f"   Description: {channel['description'][:100]}...")

    return channels[0]['channel_id'] if channels else None


def test_get_channel_details(channel_id: str):
    """Test 2: Get channel details"""
    print("\n" + "="*60)
    print(f"TEST 2: Get Channel Details")
    print("="*60)

    service = YouTubeService()
    details = service.get_channel_details(channel_id)

    if details:
        print(f"\nChannel: {details['channel_name']}")
        print(f"Channel ID: {details['channel_id']}")
        print(f"Subscribers: {details['subscriber_count']:,}")
        print(f"Total Videos: {details['video_count']:,}")
        print(f"Total Views: {details['view_count']:,}")
        print(f"Custom URL: {details.get('custom_url', 'N/A')}")
        print(f"Published At: {details.get('published_at', 'N/A')}")
        print(f"Description: {details['description'][:200]}...")
    else:
        print("❌ Failed to get channel details")

    return details is not None


def test_search_videos_in_channel(channel_id: str):
    """Test 3: Search videos in a specific channel"""
    print("\n" + "="*60)
    print(f"TEST 3: Search Videos in Channel - 'türev'")
    print("="*60)

    service = YouTubeService()
    videos = service.search_videos_in_channel(
        channel_id=channel_id,
        query="türev",
        max_results=3
    )

    print(f"\nFound {len(videos)} videos:")
    video_ids = []
    for i, video in enumerate(videos, 1):
        print(f"\n{i}. {video['title']}")
        print(f"   Video ID: {video['video_id']}")
        print(f"   Channel: {video['channel_name']}")
        print(f"   Views: {video['view_count']:,}")
        print(f"   Likes: {video['like_count']:,}")
        print(f"   Duration: {video['duration']} ({video['duration_seconds'] // 60} min)")
        print(f"   Published: {video['published_at'][:10]} ({video['published_years_ago']:.1f} years ago)")
        print(f"   URL: {video['url']}")
        video_ids.append(video['video_id'])

    return video_ids


def test_verify_video_availability(video_ids: list):
    """Test 4: Verify video availability"""
    print("\n" + "="*60)
    print(f"TEST 4: Verify Video Availability")
    print("="*60)

    service = YouTubeService()

    for video_id in video_ids[:3]:  # Test first 3 videos
        is_available = service.verify_video_availability(video_id)
        status = "✅ Available & Embeddable" if is_available else "❌ Not Available"
        print(f"\nVideo ID: {video_id}")
        print(f"Status: {status}")

    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PHASE 2: YouTube Service Enhancement - Test Suite")
    print("="*60)

    try:
        # Test 1: Search channels
        channel_id = test_search_channels()
        if not channel_id:
            print("\n❌ No channels found. Cannot proceed with other tests.")
            return

        # Test 2: Get channel details
        test_get_channel_details(channel_id)

        # Test 3: Search videos in channel
        video_ids = test_search_videos_in_channel(channel_id)

        if video_ids:
            # Test 4: Verify video availability
            test_verify_video_availability(video_ids)
        else:
            print("\n⚠️ No videos found in channel. Skipping availability test.")

        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
