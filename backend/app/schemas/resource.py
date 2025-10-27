"""
Pydantic schemas for resources
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ResourceBase(BaseModel):
    """Base resource schema"""
    name: str
    type: str  # 'youtube', 'pdf', 'website'
    url: str
    description: Optional[str] = None
    subject_name: Optional[str] = None
    topic: Optional[str] = None
    thumbnail_url: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class ResourceCreate(ResourceBase):
    """Schema for creating a resource"""
    pass


class ResourceResponse(ResourceBase):
    """Schema for resource response"""
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ResourceListResponse(BaseModel):
    """Schema for list of resources"""
    resources: List[ResourceResponse]
    total: int


class LinkResourceRequest(BaseModel):
    """Schema for linking resources to recommendation"""
    resource_ids: List[str]
