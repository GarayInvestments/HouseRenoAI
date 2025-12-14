"""
Inspection API Routes - Phase B.2

Endpoints for managing building inspections linked to permits.
Supports scheduling, status updates, photo uploads, and deficiency tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from app.db.session import get_db
from app.db.models import User
from app.routes.auth_supabase import get_current_user
from app.services.inspection_service import InspectionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inspections", tags=["inspections"])


# Pydantic Models
class InspectionCreate(BaseModel):
    """Request model for creating an inspection"""
    permit_id: UUID
    project_id: UUID
    inspection_type: str
    scheduled_date: Optional[datetime] = None
    status: str = "Scheduled"
    inspector: Optional[str] = None
    notes: Optional[str] = None
    extra: Optional[dict] = None


class InspectionUpdate(BaseModel):
    """Request model for updating an inspection"""
    inspection_type: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    status: Optional[str] = None
    inspector: Optional[str] = None
    result: Optional[str] = None
    notes: Optional[str] = None
    completed_date: Optional[datetime] = None


class InspectionResponse(BaseModel):
    """Response model for inspection data"""
    inspection_id: UUID
    business_id: str
    permit_id: UUID
    project_id: UUID
    inspection_type: str
    status: str
    scheduled_date: Optional[datetime]
    completed_date: Optional[datetime]
    inspector: Optional[str]
    assigned_to: Optional[UUID]
    result: Optional[str]
    notes: Optional[str]
    photos: Optional[dict]
    deficiencies: Optional[dict]
    extra: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InspectionListResponse(BaseModel):
    """Paginated response for inspection list"""
    items: List[InspectionResponse]
    total: int
    skip: int
    limit: int


class PhotoUpload(BaseModel):
    """Request model for uploading inspection photos"""
    url: str
    timestamp: Optional[datetime] = None
    gps: Optional[dict] = None
    notes: Optional[str] = None


class DeficiencyCreate(BaseModel):
    """Request model for adding a deficiency"""
    description: str
    severity: str = "Medium"  # Low, Medium, High, Critical
    photo_refs: Optional[List[str]] = None
    notes: Optional[str] = None


# Endpoints

@router.post("", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection(
    inspection_data: InspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new inspection for a permit.
    """
    try:
        inspection = await InspectionService.create_inspection(
            db=db,
            permit_id=str(inspection_data.permit_id),
            project_id=str(inspection_data.project_id),
            inspection_type=inspection_data.inspection_type,
            scheduled_date=inspection_data.scheduled_date,
            status=inspection_data.status,
            inspector=inspection_data.inspector,
            extra=inspection_data.extra or {}
        )
        
        await db.commit()
        await db.refresh(inspection)
        
        logger.info(f"Created inspection {inspection.business_id} for permit {inspection_data.permit_id}")
        return inspection
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create inspection: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create inspection: {str(e)}"
        )


@router.get("", response_model=InspectionListResponse)
async def list_inspections(
    project_id: Optional[UUID] = None,
    permit_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List inspections with optional filtering.
    """
    try:
        inspections = await InspectionService.get_inspections(
            db=db,
            project_id=str(project_id) if project_id else None,
            permit_id=str(permit_id) if permit_id else None,
            status=status_filter,
            skip=skip,
            limit=limit
        )
        
        return InspectionListResponse(
            items=inspections,
            total=len(inspections),
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to list inspections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list inspections: {str(e)}"
        )


@router.get("/by-business-id/{business_id}", response_model=InspectionResponse)
async def get_inspection_by_business_id(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get an inspection by business ID (e.g., INS-00001).
    """
    try:
        inspection = await InspectionService.get_by_business_id(db, business_id)
        
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inspection {business_id} not found"
            )
        
        return inspection
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get inspection {business_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get inspection: {str(e)}"
        )


@router.get("/{inspection_id}", response_model=InspectionResponse)
async def get_inspection(
    inspection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get an inspection by UUID.
    """
    try:
        inspection = await InspectionService.get_by_id(db, str(inspection_id))
        
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inspection not found"
            )
        
        logger.info(f"Retrieved inspection {inspection.business_id}")
        return inspection
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get inspection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get inspection: {str(e)}"
        )


@router.put("/{inspection_id}", response_model=InspectionResponse)
async def update_inspection(
    inspection_id: UUID,
    update_data: InspectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an inspection.
    """
    try:
        inspection = await InspectionService.update_inspection(
            db=db,
            inspection_id=str(inspection_id),
            **update_data.model_dump(exclude_unset=True)
        )
        
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inspection not found"
            )
        
        await db.commit()
        await db.refresh(inspection)
        
        logger.info(f"Updated inspection {inspection.business_id}")
        return inspection
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update inspection: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update inspection: {str(e)}"
        )


@router.post("/{inspection_id}/photos", response_model=InspectionResponse)
async def add_inspection_photo(
    inspection_id: UUID,
    photo: PhotoUpload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a photo to an inspection.
    """
    try:
        inspection = await InspectionService.add_photo(
            db=db,
            inspection_id=str(inspection_id),
            photo_url=photo.url,
            uploaded_by=current_user.get("email"),
            timestamp=photo.timestamp,
            gps=photo.gps,
            notes=photo.notes
        )
        
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inspection not found"
            )
        
        await db.commit()
        await db.refresh(inspection)
        
        logger.info(f"Added photo to inspection {inspection.business_id}")
        return inspection
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add photo: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add photo: {str(e)}"
        )


@router.post("/{inspection_id}/deficiencies", response_model=InspectionResponse)
async def add_deficiency(
    inspection_id: UUID,
    deficiency: DeficiencyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a deficiency to an inspection.
    """
    try:
        inspection = await InspectionService.add_deficiency(
            db=db,
            inspection_id=str(inspection_id),
            description=deficiency.description,
            severity=deficiency.severity,
            photo_refs=deficiency.photo_refs,
            notes=deficiency.notes
        )
        
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inspection not found"
            )
        
        await db.commit()
        await db.refresh(inspection)
        
        logger.info(f"Added deficiency to inspection {inspection.business_id}")
        return inspection
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add deficiency: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add deficiency: {str(e)}"
        )


@router.delete("/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_inspection(
    inspection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an inspection (soft delete - sets status to 'Cancelled').
    """
    try:
        inspection = await InspectionService.cancel_inspection(
            db=db,
            inspection_id=str(inspection_id)
        )
        
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inspection not found"
            )
        
        await db.commit()
        logger.info(f"Cancelled inspection {inspection.business_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel inspection: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel inspection: {str(e)}"
        )

