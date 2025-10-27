"""
Resource service for managing study material recommendations
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import Resource, RecommendationResource, Recommendation
from app.services.youtube_service import YouTubeService
import uuid


class ResourceService:
    """Service for managing study resources"""

    def __init__(self, db: Session):
        self.db = db
        self.youtube_service = YouTubeService()

    def get_or_create_youtube_resources(
        self,
        topic: str,
        subject: str,
        count: int = 3
    ) -> List[Resource]:
        """
        Get or create YouTube video resources for a topic

        First checks if resources exist in DB (cache).
        If not, searches YouTube and creates new resources.

        Args:
            topic: Topic name (e.g., "Hücre Bölünmeleri")
            subject: Subject name (e.g., "Biyoloji")
            count: Number of resources to return

        Returns:
            List of Resource objects
        """
        # Check if we already have resources for this topic/subject
        existing = self.db.query(Resource).filter(
            and_(
                Resource.type == 'youtube',
                Resource.subject_name == subject,
                Resource.topic == topic,
                Resource.is_active == True
            )
        ).limit(count).all()

        if len(existing) >= count:
            return existing

        # Need to fetch new resources
        videos = self.youtube_service.search_videos(
            query=topic,
            subject=subject,
            max_results=count
        )

        resources = []
        for video in videos:
            # Check if this URL already exists
            existing_res = self.db.query(Resource).filter(
                Resource.url == video["url"]
            ).first()

            if existing_res:
                resources.append(existing_res)
                continue

            # Create new resource
            resource = Resource(
                id=str(uuid.uuid4()),
                name=video["title"],
                type='youtube',
                url=video["url"],
                description=video.get("description", ""),
                subject_name=subject,
                topic=topic,
                thumbnail_url=video.get("thumbnail_url"),
                extra_data={
                    "channel_name": video.get("channel_name"),
                    "view_count": video.get("view_count", 0),
                    "like_count": video.get("like_count", 0),
                },
                is_active=True
            )

            self.db.add(resource)
            resources.append(resource)

        self.db.commit()

        return resources[:count]

    def get_resources_by_subject(self, subject: str) -> List[Resource]:
        """Get all active resources for a subject"""
        return self.db.query(Resource).filter(
            and_(
                Resource.subject_name == subject,
                Resource.is_active == True
            )
        ).all()

    def get_all_resources(self, subject: Optional[str] = None) -> List[Resource]:
        """Get all active resources, optionally filtered by subject"""
        query = self.db.query(Resource).filter(Resource.is_active == True)

        if subject:
            query = query.filter(Resource.subject_name == subject)

        return query.all()

    def link_resources_to_recommendation(
        self,
        recommendation_id: str,
        resource_ids: List[str]
    ) -> bool:
        """
        Link resources to a recommendation

        Args:
            recommendation_id: ID of the recommendation
            resource_ids: List of resource IDs to link

        Returns:
            True if successful
        """
        # Verify recommendation exists
        rec = self.db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()

        if not rec:
            return False

        # Remove existing links
        self.db.query(RecommendationResource).filter(
            RecommendationResource.recommendation_id == recommendation_id
        ).delete()

        # Create new links
        for resource_id in resource_ids:
            # Verify resource exists
            resource = self.db.query(Resource).filter(
                Resource.id == resource_id
            ).first()

            if not resource:
                continue

            link = RecommendationResource(
                id=str(uuid.uuid4()),
                recommendation_id=recommendation_id,
                resource_id=resource_id
            )
            self.db.add(link)

        self.db.commit()
        return True

    def get_recommendation_resources(self, recommendation_id: str) -> List[Resource]:
        """Get all resources linked to a recommendation"""
        links = self.db.query(RecommendationResource).filter(
            RecommendationResource.recommendation_id == recommendation_id
        ).all()

        resource_ids = [link.resource_id for link in links]

        if not resource_ids:
            return []

        return self.db.query(Resource).filter(
            Resource.id.in_(resource_ids)
        ).all()

    def auto_link_resources(
        self,
        recommendation_id: str,
        subject: str,
        topic: str,
        count: int = 3
    ) -> List[Resource]:
        """
        Automatically find and link resources to a recommendation

        Args:
            recommendation_id: ID of the recommendation
            subject: Subject name
            topic: Topic name
            count: Number of resources to link

        Returns:
            List of linked resources
        """
        # Get or create resources
        resources = self.get_or_create_youtube_resources(
            topic=topic,
            subject=subject,
            count=count
        )

        if not resources:
            return []

        # Link them to the recommendation
        resource_ids = [r.id for r in resources]
        self.link_resources_to_recommendation(recommendation_id, resource_ids)

        return resources
