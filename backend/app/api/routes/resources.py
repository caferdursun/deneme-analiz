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


@router.post("/recommendations/{recommendation_id}/curate")
async def curate_resources(
    recommendation_id: str,
    db: Session = Depends(get_db),
):
    """
    Use Claude AI to curate high-quality resources for a recommendation

    - Uses Claude to intelligently find relevant resources
    - Finds YouTube videos, PDFs, and websites
    - Considers learning outcomes and high school curriculum
    - Returns resources grouped by type (youtube, pdf, website)
    """
    resource_service = ResourceService(db)

    try:
        resources_by_type = resource_service.curate_resources(
            recommendation_id=recommendation_id
        )

        # Convert to response format
        response = {
            "youtube": [ResourceResponse.from_orm(r) for r in resources_by_type.get("youtube", [])],
            "pdf": [ResourceResponse.from_orm(r) for r in resources_by_type.get("pdf", [])],
            "website": [ResourceResponse.from_orm(r) for r in resources_by_type.get("website", [])]
        }

        return response

    except Exception as e:
        print(f"Error curating resources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error curating resources: {str(e)}"
        )


@router.delete("/{resource_id}", response_model=dict)
async def delete_resource(
    resource_id: str,
    blacklist: bool = Query(True, description="Whether to add to blacklist (default: True)"),
    reason: str = Query(None, description="Optional reason for deleting"),
    db: Session = Depends(get_db),
):
    """
    Delete a resource with optional blacklisting

    - Removes resource from database
    - Optionally adds URL to blacklist so it won't be recommended again
    - Returns success message
    """
    resource_service = ResourceService(db)

    if blacklist:
        success = resource_service.delete_and_blacklist_resource(
            resource_id=resource_id,
            reason=reason
        )
        message = "Resource deleted and blacklisted successfully"
    else:
        success = resource_service.delete_resource_only(resource_id)
        message = "Resource deleted successfully"

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with id {resource_id} not found"
        )

    return {
        "message": message,
        "resource_id": resource_id,
        "blacklisted": blacklist
    }
