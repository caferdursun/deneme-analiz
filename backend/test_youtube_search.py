"""
Test script for YouTube API channel and video search
Tests finding top TYT/AYT Fizik channels and their videos about "Prizmalar"
"""
import os
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# You need to set your YouTube API key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_API_KEY_HERE")

def search_channels(query: str, max_results: int = 5):
    """Search for YouTube channels by query"""
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # Search for channels
        search_response = youtube.search().list(
            q=query,
            type='channel',
            part='id,snippet',
            maxResults=max_results,
            relevanceLanguage='tr',
            regionCode='TR'
        ).execute()

        channels = []
        channel_ids = []

        for item in search_response.get('items', []):
            channel_id = item['id']['channelId']
            channel_ids.append(channel_id)
            channels.append({
                'id': channel_id,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'][:100] + '...'
            })

        # Get detailed channel statistics
        channels_response = youtube.channels().list(
            part='statistics,snippet',
            id=','.join(channel_ids)
        ).execute()

        # Add subscriber count
        for i, channel_item in enumerate(channels_response.get('items', [])):
            stats = channel_item['statistics']
            channels[i]['subscriber_count'] = int(stats.get('subscriberCount', 0))
            channels[i]['video_count'] = int(stats.get('videoCount', 0))

        # Sort by subscriber count
        channels.sort(key=lambda x: x['subscriber_count'], reverse=True)

        return channels

    except HttpError as e:
        print(f"YouTube API Error: {e}")
        return []

def parse_duration(duration_str: str) -> int:
    """Parse ISO 8601 duration to seconds"""
    import re
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds

def search_channel_videos(channel_id: str, topic: str, max_results: int = 5):
    """Search for videos in a specific channel about a topic"""
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # Search for videos in channel about the topic
        search_response = youtube.search().list(
            q=topic,
            channelId=channel_id,
            type='video',
            part='id,snippet',
            maxResults=max_results * 4,  # Get more to filter
            relevanceLanguage='tr',
            order='viewCount'  # Sort by view count
        ).execute()

        videos = []
        video_ids = []

        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            video_ids.append(video_id)
            videos.append({
                'id': video_id,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'][:100] + '...',
                'published_at': item['snippet']['publishedAt']
            })

        if not video_ids:
            return []

        # Get detailed video statistics
        videos_response = youtube.videos().list(
            part='statistics,contentDetails',
            id=','.join(video_ids)
        ).execute()

        # Add view count and duration
        for i, video_item in enumerate(videos_response.get('items', [])):
            stats = video_item['statistics']
            videos[i]['view_count'] = int(stats.get('viewCount', 0))
            videos[i]['like_count'] = int(stats.get('likeCount', 0))
            videos[i]['duration'] = video_item['contentDetails']['duration']

        # Filter videos by relevance and quality
        filtered_videos = []
        for video in videos:
            # Check if topic is in title (case insensitive)
            if topic.lower() not in video['title'].lower():
                continue

            # Parse and check duration (5 min to 45 min)
            duration_seconds = parse_duration(video['duration'])
            if duration_seconds < 300 or duration_seconds > 2700:
                continue

            # Minimum view count
            if video['view_count'] < 5000:
                continue

            filtered_videos.append(video)

        # Sort by view count and take top N
        filtered_videos.sort(key=lambda x: x['view_count'], reverse=True)

        return filtered_videos[:max_results]

    except HttpError as e:
        print(f"YouTube API Error: {e}")
        return []

def main():
    """Test the YouTube search functionality"""
    print("=" * 80)
    print("YouTube API Test: TYT/AYT Fizik Channels & Prizmalar Videos")
    print("=" * 80)

    # Step 1: Find top TYT/AYT Fizik channels
    print("\n[1] Searching for top TYT/AYT Fizik channels...")
    channel_query = "TYT AYT Fizik"
    channels = search_channels(channel_query, max_results=5)

    if not channels:
        print("❌ No channels found or API key not configured")
        print("\nPlease set YOUTUBE_API_KEY environment variable:")
        print("export YOUTUBE_API_KEY='your-api-key-here'")
        return

    print(f"\n✓ Found {len(channels)} channels:\n")
    for i, channel in enumerate(channels, 1):
        print(f"{i}. {channel['title']}")
        print(f"   Subscribers: {channel['subscriber_count']:,}")
        print(f"   Videos: {channel['video_count']:,}")
        print(f"   ID: {channel['id']}")
        print()

    # Step 2: Search each channel for "Prizmalar" videos
    print("\n[2] Searching for 'Prizmalar' videos in each channel...\n")
    topic = "Prizmalar"

    all_results = {}

    for channel in channels:
        print(f"📺 Channel: {channel['title']}")
        videos = search_channel_videos(channel['id'], topic, max_results=5)

        if videos:
            all_results[channel['title']] = videos
            print(f"   Found {len(videos)} videos:\n")

            for i, video in enumerate(videos, 1):
                print(f"   {i}. {video['title']}")
                print(f"      Views: {video['view_count']:,}")
                print(f"      Likes: {video['like_count']:,}")
                print(f"      Duration: {video['duration']}")
                print(f"      URL: https://youtube.com/watch?v={video['id']}")
                print()
        else:
            print(f"   ❌ No videos found about '{topic}'\n")

    # Step 3: Get overall top 5 videos across all channels
    print("\n[3] Overall Top 5 'Prizmalar' Videos:\n")
    all_videos = []
    for channel_name, videos in all_results.items():
        for video in videos:
            video['channel'] = channel_name
            all_videos.append(video)

    # Sort by view count
    all_videos.sort(key=lambda x: x['view_count'], reverse=True)
    top_5 = all_videos[:5]

    for i, video in enumerate(top_5, 1):
        print(f"{i}. {video['title']}")
        print(f"   Channel: {video['channel']}")
        print(f"   Views: {video['view_count']:,}")
        print(f"   URL: https://youtube.com/watch?v={video['id']}")
        print()

    # Save results to JSON
    output = {
        'channels': channels,
        'videos_by_channel': all_results,
        'top_5_overall': top_5
    }

    with open('youtube_search_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n✓ Results saved to youtube_search_results.json")

if __name__ == "__main__":
    main()
