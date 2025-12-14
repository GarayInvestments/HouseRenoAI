"""
Pydantic models for licensed_businesses API routes.
Phase Q.3: API Endpoints
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LicensedBusinessCreate(BaseModel):
    """Request model for creating a licensed business."""
    business_name: str
    license_number: str
    license_state: str  # e.g., "NC"
    business_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    license_type: Optional[str] = None  # GENERAL_CONTRACTOR, BUILDING_CONTRACTOR, etc.
    license_issue_date: Optional[datetime] = None
    license_expiration_date: Optional[datetime] = None
    is_active: bool = True
    is_owner_company: bool = False  # True for House Renovators/2States
    notes: Optional[str] = None


class LicensedBusinessUpdate(BaseModel):
    """Request model for updating a licensed business."""
    business_name: Optional[str] = None
    license_number: Optional[str] = None
    license_state: Optional[str] = None
    business_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    license_type: Optional[str] = None
    license_issue_date: Optional[datetime] = None
    license_expiration_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_owner_company: Optional[bool] = None
    notes: Optional[str] = None
