"""
YouTube service for resource recommendations
Uses YouTube Data API v3 for dynamic video search
"""
from typing import List, Dict, Optional
import requests
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
