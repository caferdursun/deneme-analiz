"""
YouTubeChannel model for managing trusted educational YouTube channels
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text
from datetime import datetime
import uuid

from app.core.database import Base


class YouTubeChannel(Base):
    """YouTube channel for educational content"""

    __tablename__ = "youtube_channels"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # YouTube channel information
    channel_id = Column(String(100), unique=True, nullable=False, index=True)
    channel_name = Column(String(255), nullable=False)
    custom_url = Column(String(255))  # e.g., @TongucAkademi

    # Subject categorization
    subject_name = Column(String(50), nullable=False, index=True)  # Matematik, Fizik, etc.

    # Channel statistics
    subscriber_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)

    # Channel metadata
    description = Column(Text)
    thumbnail_url = Column(String(500))

    # Quality and trust scoring
    trust_score = Column(Float, default=70.0)  # 0-100 scale
    is_active = Column(Boolean, default=True, index=True)

    # Tracking
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Discovery metadata
    discovered_via = Column(String(100))  # 'auto_search', 'manual_add', etc.
    notes = Column(Text)  # Admin notes about this channel

    def __repr__(self):
        return f"<YouTubeChannel(name='{self.channel_name}', subject='{self.subject_name}', subscribers={self.subscriber_count})>"
