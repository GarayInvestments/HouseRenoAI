"""
Pydantic models for oversight_actions API routes.
Phase Q.3: API Endpoints
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OversightActionCreate(BaseModel):
    """Request model for creating an oversight action."""
    project_id: str  # UUID of project
    site_visit_id: Optional[str] = None  # UUID of site visit if applicable
    licensed_business_id: str  # UUID of licensed business
    qualifier_id: str  # UUID of qualifier
    action_type: str  # SITE_VISIT, PLAN_REVIEW, INSPECTION_ATTENDANCE, PERMITTING, CONSULTATION
    action_date: datetime
    action_description: Optional[str] = None
    location: Optional[str] = None
    duration_hours: Optional[float] = None
    attendees: Optional[List[dict]] = None  # JSONB array: [{"name": "...", "role": "..."}]
    photos: Optional[List[dict]] = None  # JSONB array: [{"url": "...", "description": "..."}]
    notes: Optional[str] = None
    follow_up_required: bool = False
    follow_up_notes: Optional[str] = None


class OversightActionUpdate(BaseModel):
    """Request model for updating an oversight action."""
    site_visit_id: Optional[str] = None
    action_type: Optional[str] = None
    action_date: Optional[datetime] = None
    action_description: Optional[str] = None
    location: Optional[str] = None
    duration_hours: Optional[float] = None
    attendees: Optional[List[dict]] = None
    photos: Optional[List[dict]] = None
    notes: Optional[str] = None
    follow_up_required: Optional[bool] = None
    follow_up_notes: Optional[str] = None
