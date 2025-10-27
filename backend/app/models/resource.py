"""
Resource model for study material recommendations
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, Float
from datetime import datetime
import uuid

from app.core.database import Base


class Resource(Base):
    """Study resource model (YouTube videos, PDFs, websites)"""

    __tablename__ = "resources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Basic info
    name = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)  # 'youtube', 'pdf', 'website'
    url = Column(String(500), nullable=False)
    description = Column(Text)

    # Categorization
    subject_name = Column(String(50))  # For filtering by subject
    topic = Column(String(255))  # For matching with recommendations

    # YouTube specific
    thumbnail_url = Column(String(500))  # YouTube thumbnail
    extra_data = Column(JSON)  # {view_count, subscriber_count, channel_name, duration, etc.}

    # Quality and relevance (NEW)
    learning_outcome_ids = Column(JSON)  # List of learning outcome IDs this resource covers
    quality_score = Column(Float, default=50.0)  # 0-100 score based on Claude + metadata
    education_level = Column(String(20), default='lise')  # 'lise', 'üniversite', etc.
    curator_notes = Column(Text)  # Claude's reasoning for why this resource is relevant

    # Status
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Resource(type='{self.type}', name='{self.name}', quality={self.quality_score})>"
