"""
Resources API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.services.resource_service import ResourceService
from app.schemas.resource import (
    ResourceListResponse,
    ResourceResponse,
    LinkResourceRequest,
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


@router.get("/subject/{subject}", response_model=ResourceListResponse)
async def get_resources_by_subject(
    subject: str,
    db: Session = Depends(get_db),
):
    """
    Get all resources for a specific subject

    - Returns resources filtered by subject name
    """
    resource_service = ResourceService(db)
    resources = resource_service.get_resources_by_subject(subject)

    return ResourceListResponse(
        resources=resources,
        total=len(resources)
    )


@router.get("/recommendations/{recommendation_id}", response_model=List[ResourceResponse])
async def get_recommendation_resources(
    recommendation_id: str,
    db: Session = Depends(get_db),
):
    """
    Get all resources linked to a recommendation

    - Returns resources associated with the given recommendation
    """
    resource_service = ResourceService(db)
    resources = resource_service.get_recommendation_resources(recommendation_id)

    return resources


@router.post("/recommendations/{recommendation_id}/auto-link", response_model=List[ResourceResponse])
async def auto_link_resources(
    recommendation_id: str,
    subject: str = Query(..., description="Subject name"),
    topic: str = Query(..., description="Topic name"),
    count: int = Query(3, description="Number of resources to link"),
    db: Session = Depends(get_db),
):
    """
    Automatically find and link resources to a recommendation

    - Searches for relevant YouTube videos
    - Creates resource entries if they don't exist
    - Links them to the recommendation
    - Returns the linked resources
    """
    resource_service = ResourceService(db)

    try:
        resources = resource_service.auto_link_resources(
            recommendation_id=recommendation_id,
            subject=subject,
            topic=topic,
            count=count
        )

        return resources

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error auto-linking resources: {str(e)}"
        )


@router.post("/recommendations/{recommendation_id}/link", response_model=dict)
async def link_resources(
    recommendation_id: str,
    request: LinkResourceRequest,
    db: Session = Depends(get_db),
):
    """
    Manually link specific resources to a recommendation

    - Accepts a list of resource IDs
    - Links them to the recommendation
    - Replaces any existing links
    """
    resource_service = ResourceService(db)

    success = resource_service.link_resources_to_recommendation(
        recommendation_id=recommendation_id,
        resource_ids=request.resource_ids
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation with id {recommendation_id} not found"
        )

    return {
        "message": "Resources linked successfully",
        "recommendation_id": recommendation_id,
        "resource_count": len(request.resource_ids)
    }
