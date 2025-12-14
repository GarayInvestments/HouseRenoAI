"""
Pydantic models for qualifiers API routes.
Phase Q.3: API Endpoints
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class QualifierCreate(BaseModel):
    """Request model for creating a qualifier."""
    user_id: str  # Must be valid UUID from users table
    qualifier_license_number: str  # NC qualifier ID
    qualifier_license_state: str  # e.g., "NC"
    max_licenses_allowed: int = 2  # Default per NC law
    current_license_count: int = 0
    is_active: bool = True
    qualification_date: Optional[datetime] = None
    qualification_expiration: Optional[datetime] = None
    notes: Optional[str] = None


class QualifierUpdate(BaseModel):
    """Request model for updating a qualifier."""
    qualifier_license_number: Optional[str] = None
    qualifier_license_state: Optional[str] = None
    max_licenses_allowed: Optional[int] = None
    current_license_count: Optional[int] = None
    is_active: Optional[bool] = None
    qualification_date: Optional[datetime] = None
    qualification_expiration: Optional[datetime] = None
    notes: Optional[str] = None


class QualifierAssignmentCreate(BaseModel):
    """Request model for assigning a qualifier to a licensed business."""
    licensed_business_id: str  # UUID of licensed business
    qualifier_id: str  # UUID of qualifier
    start_date: date
    end_date: Optional[date] = None  # NULL = active assignment
    cutoff_date: Optional[date] = None  # Auto-calculated as end_date + 30 days
    is_primary: bool = True
    assignment_notes: Optional[str] = None


class QualifierAssignmentUpdate(BaseModel):
    """Request model for updating a qualifier assignment."""
    end_date: Optional[date] = None
    cutoff_date: Optional[date] = None
    is_primary: Optional[bool] = None
    assignment_notes: Optional[str] = None
