"""
Junction table for Recommendation-Resource many-to-many relationship
"""
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class RecommendationResource(Base):
    """Links recommendations to study resources"""

    __tablename__ = "recommendation_resources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    recommendation_id = Column(String(36), ForeignKey("recommendations.id"), nullable=False, index=True)
    resource_id = Column(String(36), ForeignKey("resources.id"), nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    recommendation = relationship("Recommendation", backref="recommendation_resources")
    resource = relationship("Resource", backref="recommendation_resources")

    def __repr__(self):
        return f"<RecommendationResource(rec={self.recommendation_id}, res={self.resource_id})>"
