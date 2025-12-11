"""
Permit API Routes (Phase B.1)

PostgreSQL-backed permit management endpoints.
Replaces Google Sheets integration with database operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
import logging

from app.db.session import get_db
from app.db.models import Permit
from app.routes.auth import get_current_user
from app.services.permit_service import PermitService
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class PermitCreate(BaseModel):
    """Request model for creating a permit"""
    project_id: UUID
    permit_type: str = Field(..., description="Building, Electrical, Plumbing, Mechanical, etc.")
    jurisdiction: Optional[str] = None
    permit_number: Optional[str] = None
    application_date: Optional[datetime] = None
    issuing_authority: Optional[str] = None
    inspector_name: Optional[str] = None
    notes: Optional[str] = None


class PermitUpdate(BaseModel):
    """Request model for updating a permit"""
    permit_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    permit_number: Optional[str] = None
    status: Optional[str] = None
    application_date: Optional[datetime] = None
    approval_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    issuing_authority: Optional[str] = None
    inspector_name: Optional[str] = None
    notes: Optional[str] = None


class PermitStatusUpdate(BaseModel):
    """Request model for updating permit status"""
    status: str = Field(..., description="Draft, Submitted, Under Review, Approved, Rejected, Expired")
    notes: Optional[str] = None


class PermitSubmit(BaseModel):
    """Request model for submitting a permit"""
    application_date: Optional[datetime] = None
    notes: Optional[str] = None


class PermitResponse(BaseModel):
    """Response model for permit data"""
    permit_id: UUID  # Changed from 'id' to match database model
    business_id: str
    project_id: UUID
    client_id: Optional[UUID]
    permit_number: Optional[str]
    permit_type: str
    status: str
    application_date: Optional[datetime]
    approval_date: Optional[datetime]
    expiration_date: Optional[datetime]
    issuing_authority: Optional[str]
    inspector_name: Optional[str]
    notes: Optional[str]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    extra: Optional[dict]  # JSONB field containing jurisdiction and other dynamic data
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermitListResponse(BaseModel):
    """Paginated response for permit list"""
    items: List[PermitResponse]
    total: int
    skip: int
    limit: int


class PrecheckResult(BaseModel):
    """Response model for permit precheck"""
    can_schedule: bool
    missing: List[str]
    warnings: List[str]
    ai_confidence: float
    suggestions: List[str]


# ============================================================================
# Endpoints
# ============================================================================


@router.post("", response_model=PermitResponse, status_code=status.HTTP_201_CREATED)
async def create_permit(
    permit_data: PermitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new permit for a project.
    
    Returns the created permit with auto-generated business_id (PER-00001).
    """
    try:
        permit = await PermitService.create_permit(
            db=db,
            project_id=str(permit_data.project_id),
            permit_type=permit_data.permit_type,
            permit_number=permit_data.permit_number,
            status="Draft",
            application_date=permit_data.application_date,
            extra={
                "jurisdiction": permit_data.jurisdiction,
                "issuing_authority": permit_data.issuing_authority,
                "inspector_name": permit_data.inspector_name,
                "notes": permit_data.notes
            }
        )
        
        return permit
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create permit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create permit: {str(e)}"
        )


@router.get("", response_model=PermitListResponse)
async def list_permits(
    project_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List permits with optional filtering.
    """
    try:
        permits = await PermitService.get_permits(
            db=db,
            project_id=str(project_id) if project_id else None,
            status=status_filter,
            skip=skip,
            limit=limit
        )
        
        # Apply jurisdiction filter if needed (stored in extra field)
        if jurisdiction:
            permits = [p for p in permits if p.extra and p.extra.get('jurisdiction') == jurisdiction]
        
        return PermitListResponse(
            items=permits,
            total=len(permits),
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to list permits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list permits: {str(e)}"
        )


@router.get("/by-business-id/{business_id}", response_model=PermitResponse)
async def get_permit_by_business_id(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a permit by business ID (e.g., PER-00001).
    """
    try:
        permit = await PermitService.get_by_business_id(db, business_id)
        
        if not permit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permit {business_id} not found"
            )
        
        return permit
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get permit {business_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get permit: {str(e)}"
        )


@router.get("/{permit_id}", response_model=PermitResponse)
async def get_permit(
    permit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a permit by ID.
    """
    try:
        permit = await PermitService.get_by_id(db, str(permit_id))
        
        if not permit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permit {permit_id} not found"
            )
        
        return permit
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get permit {permit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get permit: {str(e)}"
        )


@router.put("/{permit_id}", response_model=PermitResponse)
async def update_permit(
    permit_id: UUID,
    permit_data: PermitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a permit's details (does not change status).
    """
    try:
        permit = await PermitService.get_by_id(db, str(permit_id))
        
        if not permit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permit {permit_id} not found"
            )
        
        # Update core fields
        if permit_data.permit_type:
            permit.permit_type = permit_data.permit_type
        if permit_data.permit_number:
            permit.permit_number = permit_data.permit_number
        if permit_data.application_date:
            permit.application_date = permit_data.application_date
        
        # Update extra JSONB fields
        extra = permit.extra or {}
        if permit_data.jurisdiction:
            extra['jurisdiction'] = permit_data.jurisdiction
        if permit_data.issuing_authority:
            extra['issuing_authority'] = permit_data.issuing_authority
        if permit_data.inspector_name:
            extra['inspector_name'] = permit_data.inspector_name
        if permit_data.notes:
            extra['notes'] = permit_data.notes
        permit.extra = extra
        
        permit.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(permit)
        
        return permit
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update permit {permit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update permit: {str(e)}"
        )


@router.put("/{permit_id}/status", response_model=PermitResponse)
async def update_permit_status(
    permit_id: UUID,
    status_data: PermitStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a permit's status with history tracking.
    """
    try:
        # Get current permit
        permit = await PermitService.get_by_id(db, str(permit_id))
        
        if not permit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permit {permit_id} not found"
            )
        
        # Update status
        updated_permit = await PermitService.update_status(
            db=db,
            permit_id=str(permit_id),
            new_status=status_data.status,
            notes=status_data.notes
        )
        
        return updated_permit
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update permit status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update permit status: {str(e)}"
        )


@router.post("/{permit_id}/submit", response_model=PermitResponse)
async def submit_permit(
    permit_id: UUID,
    submit_data: PermitSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Submit a permit for review (changes status from Draft to Submitted).
    """
    try:
        # Get current permit
        permit = await PermitService.get_by_id(db, str(permit_id))
        
        if not permit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permit {permit_id} not found"
            )
        
        if permit.status != "Draft":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Can only submit permits in Draft status (current: {permit.status})"
            )
        
        # Update application date if provided
        if submit_data.application_date:
            permit.application_date = submit_data.application_date
        elif not permit.application_date:
            permit.application_date = datetime.now(timezone.utc)
            await db.commit()
        
        # Update status to Submitted
        updated_permit = await PermitService.update_status(
            db=db,
            permit_id=str(permit_id),
            new_status="Submitted",
            notes=submit_data.notes or "Permit submitted for review"
        )
        
        return updated_permit
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit permit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit permit: {str(e)}"
        )


@router.get("/{permit_id}/precheck", response_model=PrecheckResult)
async def precheck_permit(
    permit_id: UUID,
    inspection_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Run AI-powered precheck to determine if inspection can be scheduled.
    
    Placeholder implementation - full AI precheck in Phase B.3.
    """
    try:
        permit = await PermitService.get_by_id(db, str(permit_id))
        
        if not permit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permit {permit_id} not found"
            )
        
        # Basic validation
        missing = []
        warnings = []
        
        if permit.status != "Approved":
            missing.append(f"Permit must be Approved (current status: {permit.status})")
        
        if not permit.approval_date:
            warnings.append("Permit approval date not recorded")
        
        # TODO: Phase B.3 - Full AI precheck implementation
        # - Check jurisdiction requirements
        # - Check prior inspections
        # - Check required documents
        # - Check expiration
        
        can_schedule = len(missing) == 0
        
        return PrecheckResult(
            can_schedule=can_schedule,
            missing=missing,
            warnings=warnings,
            ai_confidence=0.85 if can_schedule else 0.95,
            suggestions=[
                "Ensure all required documents are uploaded",
                "Verify permit fees are paid before scheduling"
            ] if not can_schedule else []
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to run precheck: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run precheck: {str(e)}"
        )


@router.delete("/{permit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permit(
    permit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a permit (soft delete - changes status to Cancelled).
    """
    try:
        permit = await PermitService.get_by_id(db, str(permit_id))
        
        if not permit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permit {permit_id} not found"
            )
        
        if permit.status not in ["Draft", "Submitted"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete permit in {permit.status} status"
            )
        
        # Soft delete by changing status
        await PermitService.update_status(
            db=db,
            permit_id=str(permit_id),
            new_status="Cancelled",
            notes="Permit cancelled by user"
        )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete permit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete permit: {str(e)}"
        )
