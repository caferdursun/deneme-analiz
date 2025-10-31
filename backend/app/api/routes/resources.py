"""
Resources API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict

from app.core.database import get_db
from app.services.resource_service import ResourceService
from app.schemas.resource import (
    ResourceListResponse,
    ResourceResponse,
)

router = APIRouter()


@router.get("", response_model=ResourceListResponse)
async def get_resources(
    subject: Optional[str] = Query(None, description="Filter by subject name"),
    db: Session = Depends(get_db),
):
    """
    Get all active resources

    - Optionally filter by subject
    - Returns all YouTube videos, PDFs, and websites
    """
    resource_service = ResourceService(db)
    resources = resource_service.get_all_resources(subject=subject)

    return ResourceListResponse(
        resources=resources,
        total=len(resources)
    )


@router.put("/{resource_id}/pin", response_model=dict)
async def toggle_pin_resource(
    resource_id: str,
    db: Session = Depends(get_db),
):
    """
    Toggle pin status of a resource

    - Pinned resources won't be deleted on refresh
    - Pinned resources can't be deleted until unpinned
    """
    resource_service = ResourceService(db)

    new_pin_status = resource_service.toggle_pin_resource(resource_id)

    if new_pin_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with id {resource_id} not found"
        )

    return {
        "message": "Resource pinned successfully" if new_pin_status else "Resource unpinned successfully",
        "resource_id": resource_id,
        "is_pinned": new_pin_status
    }


@router.post("/pin", response_model=ResourceResponse)
async def pin_resource(
    request: dict,
    db: Session = Depends(get_db),
):
    """
    Create and pin a resource in one step

    - Creates a new resource from search results
    - Immediately pins it
    - Links to study plan item if item_id provided
    - Returns the created resource

    Request body:
    {
        "name": "Video title",
        "type": "youtube",
        "url": "https://youtube.com/watch?v=...",
        "description": "Video description",
        "subject_name": "Fizik",
        "topic": "Optik",
        "thumbnail_url": "...",
        "extra_data": {...},
        "study_plan_item_id": "uuid" (optional)
    }
    """
    resource_service = ResourceService(db)

    try:
        resource = resource_service.create_and_pin_resource(
            name=request["name"],
            resource_type=request["type"],
            url=request["url"],
            description=request.get("description"),
            subject_name=request.get("subject_name"),
            topic=request.get("topic"),
            thumbnail_url=request.get("thumbnail_url"),
            extra_data=request.get("extra_data", {}),
            study_plan_item_id=request.get("study_plan_item_id")
        )

        return ResourceResponse.from_orm(resource)

    except Exception as e:
        print(f"Error creating and pinning resource: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating and pinning resource: {str(e)}"
        )


@router.post("/study-plan-items/{item_id}/search")
async def search_study_item_resources(
    item_id: str,
    exclude_urls: str = Query(None, description="Comma-separated list of URLs to exclude temporarily"),
    db: Session = Depends(get_db),
):
    """
    Search for resources for a study plan item WITHOUT saving to database

    - Returns resource suggestions that are NOT saved to DB
    - User must pin a resource to save it permanently
    - Uses same algorithm as curate but skips DB insertion
    """
    resource_service = ResourceService(db)

    # Parse exclude_urls
    exclude_url_list = []
    if exclude_urls:
        exclude_url_list = [url.strip() for url in exclude_urls.split(",") if url.strip()]

    try:
        resources_by_type = resource_service.search_resources_for_study_item(
            study_plan_item_id=item_id,
            exclude_urls=exclude_url_list
        )

        # Return resources (only YouTube now)
        return resources_by_type

    except Exception as e:
        print(f"Error searching resources for study item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching resources for study item: {str(e)}"
        )


@router.get("/study-plan-items/{item_id}", response_model=List[ResourceResponse])
async def get_study_item_resources(
    item_id: str,
    db: Session = Depends(get_db),
):
    """
    Get all resources for a study plan item

    - If item has recommendation_id, returns resources for that recommendation
    - Returns empty list if no resources found
    """
    resource_service = ResourceService(db)
    resources = resource_service.get_study_item_resources(item_id)

    return resources


