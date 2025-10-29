"""
Channel Service - Manages YouTube channels for resource curation
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.youtube_channel import YouTubeChannel
from app.services.youtube_service import YouTubeService


class ChannelService:
    """Service for managing YouTube channels in database"""

    def __init__(self, db: Session):
        self.db = db
        self.youtube_service = YouTubeService()

    def discover_channels_for_subject(
        self,
        subject: str,
        force_refresh: bool = False
    ) -> List[YouTubeChannel]:
        """
        Bir ders için kanalları otomatik keşfet

        Algorithm:
        1. Check if channels exist in DB for this subject
        2. If exists and not force_refresh, return from DB
        3. Else, search YouTube: "{subject} AYT TYT"
        4. Get top 5-10 channels by subscriber count
        5. Save to database with trust_score=70.0, discovered_via='auto_search'
        6. Return channels

        Returns: List of YouTubeChannel objects
        """
        # Check existing channels
        existing = self.db.query(YouTubeChannel).filter(
            YouTubeChannel.subject_name == subject,
            YouTubeChannel.is_active == True
        ).all()

        if existing and not force_refresh:
            print(f"Found {len(existing)} existing channels for {subject}")
            return existing

        # Search YouTube
        print(f"Searching YouTube for '{subject} AYT TYT konu anlatımı'...")
        search_query = f"{subject} AYT TYT konu anlatımı"
        youtube_channels = self.youtube_service.search_channels(
            query=search_query,
            max_results=10
        )

        if not youtube_channels:
            print(f"No channels found for {subject}")
            return existing

        # Save to database
        saved_channels = []
        for yt_data in youtube_channels[:5]:  # Top 5 channels
            # Check if already exists
            existing_channel = self.db.query(YouTubeChannel).filter(
                YouTubeChannel.channel_id == yt_data['channel_id']
            ).first()

            if existing_channel:
                # Update existing
                existing_channel.subscriber_count = yt_data['subscriber_count']
                existing_channel.video_count = yt_data['video_count']
                existing_channel.view_count = yt_data['view_count']
                existing_channel.is_active = True
                channel = existing_channel
            else:
                # Create new
                channel = YouTubeChannel(
                    channel_id=yt_data['channel_id'],
                    channel_name=yt_data['channel_name'],
                    subject_name=subject,
                    subscriber_count=yt_data['subscriber_count'],
                    video_count=yt_data['video_count'],
                    view_count=yt_data['view_count'],
                    thumbnail_url=yt_data['thumbnail_url'],
                    description=yt_data['description'],
                    custom_url=yt_data.get('custom_url'),
                    trust_score=70.0,  # Default trust score
                    discovered_via='auto_search',
                    is_active=True
                )
                self.db.add(channel)

            saved_channels.append(channel)

        self.db.commit()
        print(f"✅ Saved {len(saved_channels)} channels for {subject}")
        return saved_channels

    def get_trusted_channels(
        self,
        subject: str,
        min_trust_score: float = 70.0,
        limit: int = 5,
        is_active: bool = True
    ) -> List[YouTubeChannel]:
        """
        Bir ders için güvenilir kanalları getir

        Query:
            WHERE subject_name = {subject}
            AND trust_score >= {min_trust_score}
            AND is_active = {is_active}
            ORDER BY subscriber_count DESC
            LIMIT {limit}
        """
        return self.db.query(YouTubeChannel).filter(
            YouTubeChannel.subject_name == subject,
            YouTubeChannel.trust_score >= min_trust_score,
            YouTubeChannel.is_active == is_active
        ).order_by(
            YouTubeChannel.subscriber_count.desc()
        ).limit(limit).all()

    def refresh_channel_stats(self, channel_id: str) -> Optional[YouTubeChannel]:
        """
        Kanal istatistiklerini güncelle

        Steps:
        1. Get channel from DB
        2. Fetch latest stats from YouTube API
        3. Update: subscriber_count, video_count, view_count, last_updated
        4. Save to DB
        5. Return updated channel
        """
        channel = self.db.query(YouTubeChannel).filter(
            YouTubeChannel.channel_id == channel_id
        ).first()

        if not channel:
            print(f"Channel {channel_id} not found in database")
            return None

        # Fetch latest stats
        details = self.youtube_service.get_channel_details(channel_id)
        if not details:
            print(f"Failed to fetch details for {channel_id}")
            return None

        # Update channel
        channel.subscriber_count = details['subscriber_count']
        channel.video_count = details['video_count']
        channel.view_count = details['view_count']
        channel.channel_name = details['channel_name']
        channel.description = details['description']
        channel.custom_url = details.get('custom_url')

        self.db.commit()
        print(f"✅ Updated stats for {channel.channel_name}")
        return channel

    def add_channel_manually(
        self,
        channel_id: str,
        subject: str,
        trust_score: float = 80.0,
        notes: Optional[str] = None
    ) -> Optional[YouTubeChannel]:
        """
        Kanal manüel olarak ekle

        Steps:
        1. Fetch channel details from YouTube
        2. Create YouTubeChannel object
        3. Set discovered_via='manual_add'
        4. Save to DB
        5. Return channel
        """
        # Check if already exists
        existing = self.db.query(YouTubeChannel).filter(
            YouTubeChannel.channel_id == channel_id
        ).first()

        if existing:
            print(f"Channel {channel_id} already exists")
            return existing

        # Fetch details
        details = self.youtube_service.get_channel_details(channel_id)
        if not details:
            print(f"Failed to fetch details for {channel_id}")
            return None

        # Create channel
        channel = YouTubeChannel(
            channel_id=channel_id,
            channel_name=details['channel_name'],
            subject_name=subject,
            subscriber_count=details['subscriber_count'],
            video_count=details['video_count'],
            view_count=details['view_count'],
            thumbnail_url=details['thumbnail_url'],
            description=details['description'],
            custom_url=details.get('custom_url'),
            trust_score=trust_score,
            discovered_via='manual_add',
            notes=notes,
            is_active=True
        )

        self.db.add(channel)
        self.db.commit()
        print(f"✅ Added {channel.channel_name} for {subject}")
        return channel

    def deactivate_channel(self, channel_id: str) -> bool:
        """
        Kanalı deaktif et (soft delete)

        Update: is_active = False
        """
        channel = self.db.query(YouTubeChannel).filter(
            YouTubeChannel.channel_id == channel_id
        ).first()

        if not channel:
            return False

        channel.is_active = False
        self.db.commit()
        print(f"✅ Deactivated {channel.channel_name}")
        return True

    def get_all_subjects_with_channels(self) -> List[str]:
        """
        Kanalı olan derslerin listesi

        SELECT DISTINCT subject_name FROM youtube_channels
        WHERE is_active = 1
        """
        results = self.db.query(YouTubeChannel.subject_name).filter(
            YouTubeChannel.is_active == True
        ).distinct().all()

        return [r[0] for r in results]

    def get_all_channels(self, is_active: Optional[bool] = True) -> List[YouTubeChannel]:
        """Get all channels, optionally filtered by active status"""
        query = self.db.query(YouTubeChannel)

        if is_active is not None:
            query = query.filter(YouTubeChannel.is_active == is_active)

        return query.order_by(
            YouTubeChannel.subject_name,
            YouTubeChannel.subscriber_count.desc()
        ).all()
