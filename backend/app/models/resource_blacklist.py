"""
Resource blacklist model for tracking user-rejected resources
"""
from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
import uuid

from app.core.database import Base


class ResourceBlacklist(Base):
    """Track resources that users have rejected/deleted"""

    __tablename__ = "resource_blacklist"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Resource identifier (URL is the key)
    url = Column(String(500), nullable=False, unique=True, index=True)

    # Original resource info (for record keeping)
    name = Column(String(255))
    type = Column(String(20))  # 'youtube', 'pdf', 'website'
    subject_name = Column(String(50))
    topic = Column(String(255))

    # Blacklist metadata
    reason = Column(Text)  # Optional: why was it blacklisted
    blacklisted_by = Column(String(50), default='user')  # 'user', 'system', 'admin'

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ResourceBlacklist(url='{self.url}', type='{self.type}')>"
