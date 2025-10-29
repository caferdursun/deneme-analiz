"""
YouTube service for resource recommendations
Uses YouTube Data API v3 for dynamic video search
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
import isodate
from app.core.config import settings


class YouTubeService:
    """Service for searching YouTube videos in Turkish"""

    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def search_videos(
        self,
        query: str,
        subject: str,
        max_results: int = 3
    ) -> List[Dict]:
        """
        Search for Turkish educational videos on YouTube

        Args:
            query: Search query (topic name)
            subject: Subject name for context
            max_results: Maximum number of results to return

        Returns:
            List of video dictionaries with id, title, description, channel, thumbnail, etc.
        """
        if not self.api_key:
            # Return static fallback resources if no API key
            return self._get_static_resources(subject, query)

        try:
            # Search for videos
            search_url = f"{self.base_url}/search"
            search_params = {
                "part": "snippet",
                "q": f"{query} {subject} türkçe konu anlatımı",  # Turkish topic explanation
                "type": "video",
                "regionCode": "TR",  # Turkey
                "relevanceLanguage": "tr",  # Turkish
                "order": "viewCount",  # Most viewed
                "videoDuration": "medium",  # 4-20 minutes
                "maxResults": max_results,
                "key": self.api_key
            }

            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            search_data = response.json()

            if not search_data.get("items"):
                return self._get_static_resources(subject, query)

            # Get video IDs
            video_ids = [item["id"]["videoId"] for item in search_data["items"]]

            # Get video statistics
            stats_url = f"{self.base_url}/videos"
            stats_params = {
                "part": "statistics,contentDetails",
                "id": ",".join(video_ids),
                "key": self.api_key
            }

            stats_response = requests.get(stats_url, params=stats_params, timeout=10)
            stats_response.raise_for_status()
            stats_data = stats_response.json()

            # Combine search results with statistics
            videos = []
            stats_dict = {item["id"]: item for item in stats_data.get("items", [])}

            for item in search_data["items"]:
                video_id = item["id"]["videoId"]
                snippet = item["snippet"]
                stats = stats_dict.get(video_id, {})

                video = {
                    "video_id": video_id,
                    "title": snippet["title"],
                    "description": snippet.get("description", ""),
                    "channel_name": snippet["channelTitle"],
                    "thumbnail_url": snippet["thumbnails"]["medium"]["url"],  # 320x180
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "view_count": int(stats.get("statistics", {}).get("viewCount", 0)),
                    "like_count": int(stats.get("statistics", {}).get("likeCount", 0)),
                }

                videos.append(video)

            return videos

        except Exception as e:
            print(f"YouTube API error: {e}")
            # Fallback to static resources
            return self._get_static_resources(subject, query)

    def _get_static_resources(self, subject: str, query: str) -> List[Dict]:
        """
        Get static Turkish educational resources (fallback when API unavailable)

        Returns curated Turkish YouTube channels and resources
        """
        # Popular Turkish educational YouTube channels
        static_resources = {
            "Matematik": [
                {
                    "title": "Matematik - Khan Academy Türkçe",
                    "description": "Khan Academy'nin Türkçe matematik konu anlatımları",
                    "channel_name": "Khan Academy Türkçe",
                    "url": "https://tr.khanacademy.org/math",
                    "thumbnail_url": "https://i.ytimg.com/vi/default/mqdefault.jpg",
                },
                {
                    "title": f"{query} - Matematik Konu Anlatımı",
                    "description": "Detaylı konu anlatımı ve örnek sorular",
                    "channel_name": "Tonguç Akademi",
                    "url": f"https://www.youtube.com/results?search_query={query}+matematik+tonguç",
                    "thumbnail_url": "https://i.ytimg.com/vi/default/mqdefault.jpg",
                },
            ],
            "Fizik": [
                {
                    "title": f"{query} - Fizik Konu Anlatımı",
                    "description": "Görsel destekli fizik konu anlatımı",
                    "channel_name": "Fizik Dersi",
                    "url": f"https://www.youtube.com/results?search_query={query}+fizik+konu+anlatımı",
                    "thumbnail_url": "https://i.ytimg.com/vi/default/mqdefault.jpg",
                },
            ],
            "Kimya": [
                {
                    "title": f"{query} - Kimya Konu Anlatımı",
                    "description": "Detaylı kimya konu anlatımı",
                    "channel_name": "Kimya Dersi",
                    "url": f"https://www.youtube.com/results?search_query={query}+kimya+konu+anlatımı",
                    "thumbnail_url": "https://i.ytimg.com/vi/default/mqdefault.jpg",
                },
            ],
            "Biyoloji": [
                {
                    "title": f"{query} - Biyoloji Konu Anlatımı",
                    "description": "Görsellerle biyoloji konu anlatımı",
                    "channel_name": "Biyoloji Dersi",
                    "url": f"https://www.youtube.com/results?search_query={query}+biyoloji+konu+anlatımı",
                    "thumbnail_url": "https://i.ytimg.com/vi/default/mqdefault.jpg",
                },
            ],
            "Türkçe": [
                {
                    "title": f"{query} - Türkçe Konu Anlatımı",
                    "description": "Türkçe dil bilgisi ve edebiyat",
                    "channel_name": "Türkçe Dersleri",
                    "url": f"https://www.youtube.com/results?search_query={query}+türkçe+konu+anlatımı",
                    "thumbnail_url": "https://i.ytimg.com/vi/default/mqdefault.jpg",
                },
            ],
        }

        resources = static_resources.get(subject, [])
        if not resources:
            # Generic fallback
            resources = [{
                "title": f"{query} - {subject} Konu Anlatımı",
                "description": f"{subject} dersine ait {query} konusunun anlatımı",
                "channel_name": "Eğitim Kanalları",
                "url": f"https://www.youtube.com/results?search_query={query}+{subject}+konu+anlatımı",
                "thumbnail_url": "https://i.ytimg.com/vi/default/mqdefault.jpg",
            }]

        return resources[:3]  # Return max 3 resources

    def search_channels(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        YouTube'da kanal ara, abone sayısına göre sırala

        Args:
            query: Arama kelimesi (örn: "Matematik AYT TYT")
            max_results: Max kanal sayısı

        Returns:
            List of dicts with: channel_id, channel_name, subscriber_count,
                               video_count, thumbnail_url, description
        """
        if not self.api_key:
            return []

        try:
            # Search for channels
            search_url = f"{self.base_url}/search"
            search_params = {
                "part": "snippet",
                "type": "channel",
                "q": query,
                "regionCode": "TR",
                "relevanceLanguage": "tr",
                "order": "viewCount",  # Most viewed channels
                "maxResults": max_results,
                "key": self.api_key
            }

            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            search_data = response.json()

            if not search_data.get("items"):
                return []

            # Get channel IDs
            channel_ids = [item["id"]["channelId"] for item in search_data["items"]]

            # Get detailed channel info (statistics)
            channels_url = f"{self.base_url}/channels"
            channels_params = {
                "part": "statistics,snippet",
                "id": ",".join(channel_ids),
                "key": self.api_key
            }

            channels_response = requests.get(channels_url, params=channels_params, timeout=10)
            channels_response.raise_for_status()
            channels_data = channels_response.json()

            # Format results
            channels = []
            for item in channels_data.get("items", []):
                channel = {
                    "channel_id": item["id"],
                    "channel_name": item["snippet"]["title"],
                    "subscriber_count": int(item["statistics"].get("subscriberCount", 0)),
                    "video_count": int(item["statistics"].get("videoCount", 0)),
                    "view_count": int(item["statistics"].get("viewCount", 0)),
                    "thumbnail_url": item["snippet"]["thumbnails"]["medium"]["url"],
                    "description": item["snippet"].get("description", ""),
                    "custom_url": item["snippet"].get("customUrl", "")
                }
                channels.append(channel)

            # Sort by subscriber count (highest first)
            channels.sort(key=lambda x: x["subscriber_count"], reverse=True)

            return channels

        except Exception as e:
            print(f"YouTube channel search error: {e}")
            return []

    def get_channel_details(self, channel_id: str) -> Optional[Dict]:
        """
        Kanal istatistiklerini getir

        Returns: channel_name, subscriber_count, video_count, view_count,
                 thumbnail_url, description, custom_url
        """
        if not self.api_key:
            return None

        try:
            channels_url = f"{self.base_url}/channels"
            params = {
                "part": "statistics,snippet",
                "id": channel_id,
                "key": self.api_key
            }

            response = requests.get(channels_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            if not items:
                return None

            item = items[0]
            return {
                "channel_id": item["id"],
                "channel_name": item["snippet"]["title"],
                "subscriber_count": int(item["statistics"].get("subscriberCount", 0)),
                "video_count": int(item["statistics"].get("videoCount", 0)),
                "view_count": int(item["statistics"].get("viewCount", 0)),
                "thumbnail_url": item["snippet"]["thumbnails"]["medium"]["url"],
                "description": item["snippet"].get("description", ""),
                "custom_url": item["snippet"].get("customUrl", ""),
                "published_at": item["snippet"].get("publishedAt", "")
            }

        except Exception as e:
            print(f"YouTube channel details error: {e}")
            return None

    def search_videos_in_channel(
        self,
        channel_id: str,
        query: str,
        max_results: int = 3
    ) -> List[Dict]:
        """
        Belirli bir kanalda video ara

        Filters:
            - Duration: 5-30 minutes
            - View count: >5000
            - Published: last 3 years

        Returns: video_id, title, description, thumbnail_url, channel_name,
                 view_count, like_count, duration, published_at
        """
        if not self.api_key:
            return []

        try:
            # Calculate date 3 years ago
            three_years_ago = datetime.utcnow() - timedelta(days=3*365)
            published_after = three_years_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Search for videos in the channel
            search_url = f"{self.base_url}/search"
            search_params = {
                "part": "snippet",
                "channelId": channel_id,
                "q": query,
                "type": "video",
                "order": "relevance",
                "publishedAfter": published_after,
                "maxResults": max_results * 3,  # Get more to filter later
                "key": self.api_key
            }

            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            search_data = response.json()

            if not search_data.get("items"):
                return []

            # Get video IDs
            video_ids = [item["id"]["videoId"] for item in search_data["items"]]

            # Get video statistics and details
            videos_url = f"{self.base_url}/videos"
            videos_params = {
                "part": "statistics,contentDetails,snippet",
                "id": ",".join(video_ids),
                "key": self.api_key
            }

            videos_response = requests.get(videos_url, params=videos_params, timeout=10)
            videos_response.raise_for_status()
            videos_data = videos_response.json()

            # Format and filter results
            videos = []
            for item in videos_data.get("items", []):
                try:
                    # Parse duration
                    duration_iso = item["contentDetails"]["duration"]
                    duration = isodate.parse_duration(duration_iso)
                    duration_seconds = int(duration.total_seconds())
                    duration_minutes = duration_seconds / 60

                    # Get view count
                    view_count = int(item["statistics"].get("viewCount", 0))

                    # Apply filters
                    # Duration: 5-30 minutes
                    if not (5 <= duration_minutes <= 30):
                        continue

                    # View count: >5000
                    if view_count < 5000:
                        continue

                    # Calculate years ago
                    published_at = datetime.fromisoformat(
                        item["snippet"]["publishedAt"].replace("Z", "+00:00")
                    )
                    years_ago = (datetime.utcnow().replace(tzinfo=published_at.tzinfo) - published_at).days / 365

                    video = {
                        "video_id": item["id"],
                        "title": item["snippet"]["title"],
                        "description": item["snippet"].get("description", ""),
                        "thumbnail_url": item["snippet"]["thumbnails"]["medium"]["url"],
                        "channel_name": item["snippet"]["channelTitle"],
                        "view_count": view_count,
                        "like_count": int(item["statistics"].get("likeCount", 0)),
                        "duration": duration_iso,
                        "duration_seconds": duration_seconds,
                        "published_at": item["snippet"]["publishedAt"],
                        "published_years_ago": years_ago,
                        "url": f"https://www.youtube.com/watch?v={item['id']}"
                    }

                    videos.append(video)

                except Exception as e:
                    print(f"Error processing video {item.get('id')}: {e}")
                    continue

            # Sort by view count and return top results
            videos.sort(key=lambda x: x["view_count"], reverse=True)
            return videos[:max_results]

        except Exception as e:
            print(f"YouTube video search in channel error: {e}")
            return []

    def verify_video_availability(self, video_id: str) -> bool:
        """
        Video var mı, oynatılabilir mi kontrol et

        Checks:
            - Video exists
            - embeddable: true
            - Not private/deleted

        Returns: True if available and embeddable
        """
        if not self.api_key:
            return False

        try:
            videos_url = f"{self.base_url}/videos"
            params = {
                "part": "status",
                "id": video_id,
                "key": self.api_key
            }

            response = requests.get(videos_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            if not items:
                return False

            status = items[0].get("status", {})

            # Check if video is available
            if status.get("privacyStatus") not in ["public", "unlisted"]:
                return False

            # Check if embeddable
            if not status.get("embeddable", False):
                return False

            # Check if uploadStatus is processed
            if status.get("uploadStatus") != "processed":
                return False

            return True

        except Exception as e:
            print(f"YouTube video availability check error: {e}")
            return False
