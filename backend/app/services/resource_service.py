"""
Resource service for managing study material recommendations
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import Resource, RecommendationResource, Recommendation, LearningOutcome, ResourceBlacklist, StudyPlanItem
from app.services.youtube_service import YouTubeService
from app.services.claude_curator_service import ClaudeCuratorService
from app.services.channel_service import ChannelService
import uuid


class ResourceService:
    """Service for managing study resources"""

    def __init__(self, db: Session):
        self.db = db
        self.youtube_service = YouTubeService()
        self.curator_service = ClaudeCuratorService()
        self.channel_service = ChannelService(db)

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

        # Filter out blacklisted URLs (only YouTube)
        curated_data["youtube"] = self.filter_blacklisted_urls(curated_data.get("youtube", []))

        # Filter out temporarily excluded URLs (for refresh)
        if exclude_urls:
            exclude_set = set(exclude_urls)
            curated_data["youtube"] = [r for r in curated_data["youtube"] if r.get("url") not in exclude_set]

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

        # Process and save curated resources (YouTube only)
        result = {
            "youtube": [],
            "pdf": [],
            "website": []
        }

        # Start with pinned YouTube resources only
        for pinned in pinned_resources:
            if pinned.type == "youtube":
                result["youtube"].append(pinned)

        # Process YouTube resources
        for yt_data in curated_data.get("youtube", []):
            resource = self._create_curated_resource(
                resource_data=yt_data,
                resource_type="youtube",
                subject=rec.subject_name,
                topic=rec.topic,
                learning_outcome_ids=rec.learning_outcome_ids
            )
            # Apply quality threshold: Only accept resources with score >= 55
            if resource and resource.quality_score >= 55.0:
                result["youtube"].append(resource)

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

    def curate_resources_for_study_item(
        self,
        study_plan_item_id: str,
        exclude_urls: Optional[List[str]] = None
    ) -> Dict[str, List[Resource]]:
        """
        NEW ALGORITHM - Channel-based video curation with AI-powered keywords

        Uses the new multi-stage algorithm:
        1. Get/Discover trusted channels for subject
        2. Generate search keywords using Claude
        3. Search videos in each channel with each keyword
        4. Verify availability and filter
        5. Score and rank videos
        6. Create Resource objects

        Args:
            study_plan_item_id: ID of the study plan item
            exclude_urls: Optional list of URLs to exclude temporarily

        Returns:
            Dictionary with 'youtube' resource list (pdf/website empty for now)
        """
        # 1. Get study plan item
        item = self.db.query(StudyPlanItem).filter(
            StudyPlanItem.id == study_plan_item_id
        ).first()

        if not item:
            return {"youtube": [], "pdf": [], "website": []}

        print(f"\n🎯 Curating resources for: {item.subject_name} - {item.topic}")

        # 2. Get/Discover trusted channels
        print(f"📺 Finding trusted channels for {item.subject_name}...")
        channels = self.channel_service.get_trusted_channels(
            subject=item.subject_name,
            min_trust_score=70.0,
            limit=5
        )

        # Auto-discover if no channels found
        if not channels:
            print(f"   No channels found, auto-discovering...")
            channels = self.channel_service.discover_channels_for_subject(
                subject=item.subject_name
            )

        if not channels:
            print("   ❌ No channels available")
            return {"youtube": [], "pdf": [], "website": []}

        print(f"   ✅ Found {len(channels)} channels")

        # 3. Generate search keywords using Claude
        print(f"🔍 Generating search keywords with Claude...")
        keywords = self.curator_service.generate_video_search_keywords(
            subject=item.subject_name,
            topic=item.topic,
            description=item.description,
            learning_outcome=self._get_learning_outcome_text(item)
        )
        print(f"   ✅ Generated {len(keywords)} keywords")

        # 4. Search videos in each channel with each keyword
        print(f"🎬 Searching videos in channels...")
        all_videos = []
        for channel in channels:
            for keyword in keywords:
                videos = self.youtube_service.search_videos_in_channel(
                    channel_id=channel.channel_id,
                    query=keyword,
                    max_results=3
                )

                # Add channel trust score to each video
                for video in videos:
                    video['channel_trust_score'] = channel.trust_score
                    video['channel_name_db'] = channel.channel_name

                all_videos.extend(videos)

        print(f"   Found {len(all_videos)} videos (before deduplication)")

        # 5. Verify availability (already done in search_videos_in_channel filters)
        # Videos are already filtered and verified

        # 6. Remove duplicates by video_id
        unique_videos = self._deduplicate_videos(all_videos)
        print(f"   After deduplication: {len(unique_videos)} videos")

        # 7. Score videos
        scored_videos = []
        for video in unique_videos:
            score = self._calculate_video_score(
                video=video,
                topic=item.topic,
                keywords=keywords
            )
            video['final_score'] = score
            scored_videos.append(video)

        # 8. Sort by score and filter
        top_videos = sorted(
            [v for v in scored_videos if v['final_score'] >= 55.0],
            key=lambda x: x['final_score'],
            reverse=True
        )[:10]

        print(f"   After scoring (>= 55): {len(top_videos)} videos")

        # 9. Filter out blacklisted/excluded URLs
        filtered_videos = self._filter_videos(top_videos, exclude_urls)
        print(f"   After filtering: {len(filtered_videos)} videos")

        # 10. Create Resource objects
        resources = []
        for video in filtered_videos:
            resource = self._create_resource_from_video(
                video_data=video,
                subject=item.subject_name,
                topic=item.topic,
                learning_outcome_ids=None
            )
            if resource:
                resources.append(resource)

        print(f"   ✅ Created {len(resources)} resource objects\n")

        return {"youtube": resources, "pdf": [], "website": []}

    def get_study_item_resources(self, study_plan_item_id: str) -> List[Resource]:
        """
        Get all resources for a study plan item

        If item has recommendation_id, returns resources for that recommendation.
        Otherwise, returns empty list.

        Args:
            study_plan_item_id: ID of the study plan item

        Returns:
            List of Resource objects
        """
        # Get study plan item
        item = self.db.query(StudyPlanItem).filter(
            StudyPlanItem.id == study_plan_item_id
        ).first()

        if not item or not item.recommendation_id:
            return []

        # Get resources via recommendation
        return self.get_recommendation_resources(item.recommendation_id)

    def _calculate_video_score(
        self,
        video: Dict,
        topic: str,
        keywords: List[str]
    ) -> float:
        """
        NEW SCORING ALGORITHM with engagement metrics

        Base: 50
        + Title relevance (keyword match): +15
        + Description relevance (topic match): +10
        + View count (5k-500k sweet spot): +10
        + Duration (5-30 min): +5 (already filtered)
        + Channel trust score: +15 (max)
        + Engagement (like ratio + comments): +10
        + Recency (< 3 years): +5

        Max: 110 (capped at 100)
        """
        score = 50.0

        # Title relevance
        title_lower = video.get('title', '').lower()
        topic_lower = topic.lower()
        if any(kw.lower() in title_lower for kw in keywords):
            score += 15
        elif topic_lower in title_lower:
            score += 10  # Partial credit

        # Description relevance
        desc_lower = video.get('description', '').lower()
        if topic_lower in desc_lower:
            score += 10
        elif any(word in desc_lower for word in topic_lower.split()):
            score += 5  # Partial credit

        # View count sweet spot (5K-500K)
        views = video.get('view_count', 0)
        if 5000 <= views < 500000:
            score += 10
        elif views >= 500000:
            score += 5  # Too viral might not be educational

        # Duration already filtered (5-30 min), give bonus
        score += 5

        # Channel trust score (0-100 → 0-15 points)
        channel_trust = video.get('channel_trust_score', 70.0)
        score += (channel_trust / 100) * 15

        # Engagement metrics
        like_ratio = video.get('like_ratio', 0)
        comment_count = video.get('comment_count', 0)

        # Like ratio bonus (0.3%-5% is good, >5% is excellent)
        if like_ratio >= 5.0:
            score += 7
        elif like_ratio >= 2.0:
            score += 5
        elif like_ratio >= 0.5:
            score += 3

        # Comment engagement
        if comment_count >= 100:
            score += 3
        elif comment_count >= 20:
            score += 2

        # Recency (videos already filtered to < 3 years)
        years_ago = video.get('published_years_ago', 1.5)
        if years_ago <= 1.5:
            score += 5
        elif years_ago <= 2.5:
            score += 3

        return min(score, 100.0)

    def _deduplicate_videos(self, videos: List[Dict]) -> List[Dict]:
        """Remove duplicate videos by video_id"""
        seen = set()
        unique = []
        for video in videos:
            vid_id = video.get('video_id')
            if vid_id and vid_id not in seen:
                seen.add(vid_id)
                unique.append(video)
        return unique

    def _filter_videos(
        self,
        videos: List[Dict],
        exclude_urls: Optional[List[str]]
    ) -> List[Dict]:
        """Filter blacklisted and excluded URLs"""
        # Get blacklisted URLs
        blacklisted = self.db.query(ResourceBlacklist.url).all()
        blacklisted_urls = {url[0] for url in blacklisted}

        # Combine with exclude list
        if exclude_urls:
            blacklisted_urls.update(exclude_urls)

        # Filter
        return [
            v for v in videos
            if v.get('url') not in blacklisted_urls
        ]

    def _get_learning_outcome_text(self, item: StudyPlanItem) -> Optional[str]:
        """Get learning outcome description if item has recommendation_id"""
        if not item.recommendation_id:
            return None

        rec = self.db.query(Recommendation).filter(
            Recommendation.id == item.recommendation_id
        ).first()

        if not rec or not rec.learning_outcome_ids:
            return None

        lo = self.db.query(LearningOutcome).filter(
            LearningOutcome.id == rec.learning_outcome_ids[0]
        ).first()

        return lo.outcome_description if lo else None

    def _create_resource_from_video(
        self,
        video_data: Dict,
        subject: str,
        topic: str,
        learning_outcome_ids: Optional[List[str]]
    ) -> Optional[Resource]:
        """Create Resource object from video data (real YouTube API data)"""
        url = video_data.get('url')
        if not url:
            return None

        # Check if resource already exists
        existing = self.db.query(Resource).filter(
            Resource.url == url
        ).first()

        if existing:
            return existing

        # Create new resource with real YouTube data
        resource = Resource(
            id=str(uuid.uuid4()),
            name=video_data.get('title', ''),
            type='youtube',
            url=url,
            description=video_data.get('description', '')[:500],  # Limit description
            subject_name=subject,
            topic=topic,
            thumbnail_url=video_data.get('thumbnail_url'),
            extra_data={
                "channel_name": video_data.get('channel_name'),
                "channel_name_db": video_data.get('channel_name_db'),
                "view_count": video_data.get('view_count', 0),
                "like_count": video_data.get('like_count', 0),
                "comment_count": video_data.get('comment_count', 0),
                "like_ratio": video_data.get('like_ratio', 0),
                "duration_seconds": video_data.get('duration_seconds', 0),
                "published_at": video_data.get('published_at'),
                "engagement_score": video_data.get('engagement_score', 0),
                "channel_trust_score": video_data.get('channel_trust_score', 70.0)
            },
            learning_outcome_ids=learning_outcome_ids,
            quality_score=video_data.get('final_score', 70.0),
            education_level='lise',
            curator_notes=f"Auto-curated via channel-based algorithm. Score: {video_data.get('final_score', 0):.1f}",
            is_active=True
        )

        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)

        return resource
