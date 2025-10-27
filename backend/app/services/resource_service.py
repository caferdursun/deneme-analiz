"""
Resource service for managing study material recommendations
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import Resource, RecommendationResource, Recommendation, LearningOutcome, ResourceBlacklist
from app.services.youtube_service import YouTubeService
from app.services.claude_curator_service import ClaudeCuratorService
import uuid


class ResourceService:
    """Service for managing study resources"""

    def __init__(self, db: Session):
        self.db = db
        self.youtube_service = YouTubeService()
        self.curator_service = ClaudeCuratorService()

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

    def curate_resources(
        self,
        recommendation_id: str,
        exclude_urls: Optional[List[str]] = None
    ) -> Dict[str, List[Resource]]:
        """
        Use Claude AI to curate high-quality resources for a recommendation

        Args:
            recommendation_id: ID of the recommendation
            exclude_urls: Optional list of URLs to exclude temporarily (without blacklisting)

        Returns:
            Dictionary with 'youtube', 'pdf', and 'website' resource lists
        """
        # Get recommendation details
        rec = self.db.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()

        if not rec:
            return {"youtube": [], "pdf": [], "website": []}

        # Get learning outcome details if available
        learning_outcome = None
        category = None
        subcategory = None

        if rec.learning_outcome_ids and len(rec.learning_outcome_ids) > 0:
            lo_id = rec.learning_outcome_ids[0]
            lo = self.db.query(LearningOutcome).filter(
                LearningOutcome.id == lo_id
            ).first()
            if lo:
                learning_outcome = lo.outcome_description
                category = lo.category
                subcategory = lo.subcategory

        # Use Claude to curate resources
        curated_data = self.curator_service.curate_resources(
            subject=rec.subject_name or "",
            topic=rec.topic or "",
            learning_outcome=learning_outcome,
            category=category,
            subcategory=subcategory
        )

        # Filter out blacklisted URLs
        curated_data["youtube"] = self.filter_blacklisted_urls(curated_data.get("youtube", []))
        curated_data["pdf"] = self.filter_blacklisted_urls(curated_data.get("pdf", []))
        curated_data["website"] = self.filter_blacklisted_urls(curated_data.get("website", []))

        # Filter out temporarily excluded URLs (for refresh)
        if exclude_urls:
            exclude_set = set(exclude_urls)
            curated_data["youtube"] = [r for r in curated_data["youtube"] if r.get("url") not in exclude_set]
            curated_data["pdf"] = [r for r in curated_data["pdf"] if r.get("url") not in exclude_set]
            curated_data["website"] = [r for r in curated_data["website"] if r.get("url") not in exclude_set]

        # Get existing pinned resources for this recommendation
        existing_links = self.db.query(RecommendationResource).filter(
            RecommendationResource.recommendation_id == recommendation_id
        ).all()
        existing_resource_ids = [link.resource_id for link in existing_links]

        pinned_resources = []
        if existing_resource_ids:
            pinned_resources = self.db.query(Resource).filter(
                Resource.id.in_(existing_resource_ids),
                Resource.is_pinned == True
            ).all()

        # Process and save curated resources
        result = {
            "youtube": [],
            "pdf": [],
            "website": []
        }

        # Start with pinned resources
        for pinned in pinned_resources:
            if pinned.type == "youtube":
                result["youtube"].append(pinned)
            elif pinned.type == "pdf":
                result["pdf"].append(pinned)
            elif pinned.type == "website":
                result["website"].append(pinned)

        # Process YouTube resources
        for yt_data in curated_data.get("youtube", []):
            resource = self._create_curated_resource(
                resource_data=yt_data,
                resource_type="youtube",
                subject=rec.subject_name,
                topic=rec.topic,
                learning_outcome_ids=rec.learning_outcome_ids
            )
            if resource:
                result["youtube"].append(resource)

        # Process PDF resources
        for pdf_data in curated_data.get("pdf", []):
            resource = self._create_curated_resource(
                resource_data=pdf_data,
                resource_type="pdf",
                subject=rec.subject_name,
                topic=rec.topic,
                learning_outcome_ids=rec.learning_outcome_ids
            )
            if resource:
                result["pdf"].append(resource)

        # Process website resources
        for web_data in curated_data.get("website", []):
            resource = self._create_curated_resource(
                resource_data=web_data,
                resource_type="website",
                subject=rec.subject_name,
                topic=rec.topic,
                learning_outcome_ids=rec.learning_outcome_ids
            )
            if resource:
                result["website"].append(resource)

        # Link all resources to the recommendation
        all_resource_ids = []
        for resource_list in result.values():
            all_resource_ids.extend([r.id for r in resource_list])

        if all_resource_ids:
            self.link_resources_to_recommendation(recommendation_id, all_resource_ids)

        return result

    def _create_curated_resource(
        self,
        resource_data: Dict,
        resource_type: str,
        subject: Optional[str],
        topic: Optional[str],
        learning_outcome_ids: Optional[List[str]]
    ) -> Optional[Resource]:
        """
        Create a curated resource from Claude's recommendation

        Args:
            resource_data: Resource information from Claude
            resource_type: 'youtube', 'pdf', or 'website'
            subject: Subject name
            topic: Topic name
            learning_outcome_ids: List of learning outcome IDs

        Returns:
            Created Resource object or None
        """
        url = resource_data.get("url")
        if not url:
            return None

        # Check if resource already exists
        existing = self.db.query(Resource).filter(
            Resource.url == url
        ).first()

        if existing:
            return existing

        # For YouTube, try to get additional metadata
        thumbnail_url = None
        extra_data = {}

        if resource_type == "youtube":
            try:
                video_id = url.split("watch?v=")[-1].split("&")[0]
                videos = self.youtube_service.search_videos(
                    query=resource_data.get("title", ""),
                    subject=subject or "",
                    max_results=1
                )
                if videos and videos[0].get("url") == url:
                    thumbnail_url = videos[0].get("thumbnail_url")
                    extra_data = {
                        "channel_name": videos[0].get("channel_name"),
                        "view_count": videos[0].get("view_count", 0),
                        "like_count": videos[0].get("like_count", 0),
                    }
            except:
                # Use Claude's data if YouTube API fails
                extra_data = {
                    "channel_name": resource_data.get("channel_name", ""),
                    "estimated_views": resource_data.get("estimated_views", "")
                }

        # Calculate quality score
        learning_outcome_match = bool(learning_outcome_ids)
        quality_score = self.curator_service.calculate_quality_score(
            resource_data=resource_data,
            learning_outcome_match=learning_outcome_match
        )

        # Create resource
        resource = Resource(
            id=str(uuid.uuid4()),
            name=resource_data.get("title", ""),
            type=resource_type,
            url=url,
            description=resource_data.get("description", ""),
            subject_name=subject,
            topic=topic,
            thumbnail_url=thumbnail_url,
            extra_data=extra_data,
            learning_outcome_ids=learning_outcome_ids,
            quality_score=quality_score,
            education_level='lise',
            curator_notes=resource_data.get("why_relevant", ""),
            is_active=True
        )

        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)

        return resource

    def is_url_blacklisted(self, url: str) -> bool:
        """Check if a URL is blacklisted"""
        blacklist_entry = self.db.query(ResourceBlacklist).filter(
            ResourceBlacklist.url == url
        ).first()
        return blacklist_entry is not None

    def delete_and_blacklist_resource(
        self,
        resource_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Delete a resource and add its URL to blacklist

        Args:
            resource_id: ID of the resource to delete
            reason: Optional reason for blacklisting

        Returns:
            True if successful, False if resource not found or is pinned
        """
        # Get the resource
        resource = self.db.query(Resource).filter(
            Resource.id == resource_id
        ).first()

        if not resource:
            return False

        # Don't delete pinned resources
        if resource.is_pinned:
            return False

        # Add to blacklist
        blacklist_entry = ResourceBlacklist(
            id=str(uuid.uuid4()),
            url=resource.url,
            name=resource.name,
            type=resource.type,
            subject_name=resource.subject_name,
            topic=resource.topic,
            reason=reason or "User rejected",
            blacklisted_by='user'
        )

        try:
            self.db.add(blacklist_entry)

            # Delete recommendation_resource links
            self.db.query(RecommendationResource).filter(
                RecommendationResource.resource_id == resource_id
            ).delete()

            # Delete the resource
            self.db.delete(resource)

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print(f"Error blacklisting resource: {e}")
            return False

    def delete_resource_only(self, resource_id: str) -> bool:
        """
        Delete a resource without adding to blacklist

        Args:
            resource_id: ID of the resource to delete

        Returns:
            True if successful, False if resource not found or is pinned
        """
        # Get the resource
        resource = self.db.query(Resource).filter(
            Resource.id == resource_id
        ).first()

        if not resource:
            return False

        # Don't delete pinned resources
        if resource.is_pinned:
            return False

        try:
            # Delete recommendation_resource links
            self.db.query(RecommendationResource).filter(
                RecommendationResource.resource_id == resource_id
            ).delete()

            # Delete the resource
            self.db.delete(resource)

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print(f"Error deleting resource: {e}")
            return False

    def toggle_pin_resource(self, resource_id: str) -> Optional[bool]:
        """
        Toggle pin status of a resource

        Args:
            resource_id: ID of the resource to pin/unpin

        Returns:
            New pin status (True/False) or None if resource not found
        """
        resource = self.db.query(Resource).filter(
            Resource.id == resource_id
        ).first()

        if not resource:
            return None

        try:
            resource.is_pinned = not resource.is_pinned
            self.db.commit()
            return resource.is_pinned
        except Exception as e:
            self.db.rollback()
            print(f"Error toggling pin status: {e}")
            return None

    def filter_blacklisted_urls(self, resources: List[Dict]) -> List[Dict]:
        """
        Filter out blacklisted URLs from a list of resource data

        Args:
            resources: List of resource dictionaries with 'url' key

        Returns:
            Filtered list without blacklisted URLs
        """
        if not resources:
            return []

        # Get all blacklisted URLs
        blacklisted = self.db.query(ResourceBlacklist.url).all()
        blacklisted_urls = {url[0] for url in blacklisted}

        # Filter resources
        return [r for r in resources if r.get("url") not in blacklisted_urls]
