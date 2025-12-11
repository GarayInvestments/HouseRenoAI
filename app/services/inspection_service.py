"""
Inspection Service - Business logic for inspection management.

Handles inspection CRUD, photo uploads, deficiency tracking, and precheck integration.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import logging

from app.db.models import Inspection, Permit, Project

logger = logging.getLogger(__name__)


class InspectionService:
    """Service for managing inspections and their results."""
    
    @staticmethod
    async def get_inspections(
        db: AsyncSession,
        project_id: Optional[str] = None,
        permit_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Inspection]:
        """
        Get inspections with optional filtering.
        
        Args:
            db: Database session
            project_id: Filter by project UUID
            permit_id: Filter by permit UUID
            status: Filter by inspection status
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of Inspection objects
        """
        query = select(Inspection).order_by(Inspection.scheduled_date.desc())
        
        if project_id:
            query = query.where(Inspection.project_id == project_id)
        if permit_id:
            query = query.where(Inspection.permit_id == permit_id)
        if status:
            query = query.where(Inspection.status == status)
            
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        inspections = result.scalars().all()
        
        logger.info(f"Retrieved {len(inspections)} inspections")
        return inspections
    
    @staticmethod
    async def get_by_id(db: AsyncSession, inspection_id: str) -> Optional[Inspection]:
        """Get inspection by UUID."""
        result = await db.execute(
            select(Inspection).where(Inspection.inspection_id == inspection_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_business_id(db: AsyncSession, business_id: str) -> Optional[Inspection]:
        """Get inspection by business ID (e.g., INS-00001)."""
        result = await db.execute(
            select(Inspection).where(Inspection.business_id == business_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_inspection(
        db: AsyncSession,
        permit_id: str,
        project_id: str,
        inspection_type: str,
        scheduled_date: Optional[datetime] = None,
        status: str = "Scheduled",
        inspector: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> Inspection:
        """
        Create a new inspection.
        
        Args:
            db: Database session
            permit_id: Permit UUID
            project_id: Project UUID
            inspection_type: Type of inspection (e.g., "Framing", "Final")
            scheduled_date: When inspection is scheduled
            status: Initial status (default: "Scheduled")
            inspector: Inspector name
            extra: Additional metadata
            
        Returns:
            Created Inspection object with auto-generated business_id
        """
        # Verify permit and project exist
        permit_result = await db.execute(
            select(Permit).where(Permit.permit_id == permit_id)
        )
        permit = permit_result.scalar_one_or_none()
        if not permit:
            raise ValueError(f"Permit not found: {permit_id}")
        
        project_result = await db.execute(
            select(Project).where(Project.project_id == project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        inspection = Inspection(
            permit_id=permit_id,
            project_id=project_id,
            inspection_type=inspection_type,
            scheduled_date=scheduled_date,
            status=status,
            inspector=inspector,
            photos=[],
            deficiencies=[],
            extra=extra or {}
        )
        
        db.add(inspection)
        await db.flush()
        await db.refresh(inspection)
        
        logger.info(f"Created inspection {inspection.business_id} for permit {permit.business_id}")
        return inspection
    
    @staticmethod
    async def complete_inspection(
        db: AsyncSession,
        inspection_id: str,
        result: str,
        completion_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        deficiencies: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Inspection]:
        """
        Mark inspection as complete with results.
        
        Args:
            db: Database session
            inspection_id: Inspection UUID
            result: Inspection result ("Passed", "Failed", "Conditional")
            completion_date: When inspection was completed
            notes: Inspector notes
            deficiencies: List of deficiencies found
            
        Returns:
            Updated Inspection object or None if not found
        """
        inspection = await InspectionService.get_by_id(db, inspection_id)
        if not inspection:
            return None
        
        inspection.status = "Completed"
        inspection.result = result
        inspection.completion_date = completion_date or datetime.now(timezone.utc)
        inspection.notes = notes
        inspection.updated_at = datetime.now(timezone.utc)
        
        if deficiencies:
            inspection.deficiencies = deficiencies
        
        await db.flush()
        await db.refresh(inspection)
        
        logger.info(f"Completed inspection {inspection.business_id} with result: {result}")
        return inspection
    
    @staticmethod
    async def upload_photos(
        db: AsyncSession,
        inspection_id: str,
        photos: List[Dict[str, Any]]
    ) -> Optional[Inspection]:
        """
        Add photos to inspection.
        
        Args:
            db: Database session
            inspection_id: Inspection UUID
            photos: List of photo metadata dicts with keys:
                    - url: Photo URL
                    - caption: Optional caption
                    - timestamp: When photo was taken
                    - location: Optional GPS coordinates
            
        Returns:
            Updated Inspection object or None if not found
        """
        inspection = await InspectionService.get_by_id(db, inspection_id)
        if not inspection:
            return None
        
        if not inspection.photos:
            inspection.photos = []
        
        # Add timestamp to photos if not present
        for photo in photos:
            if "timestamp" not in photo:
                photo["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        inspection.photos.extend(photos)
        inspection.updated_at = datetime.now(timezone.utc)
        
        await db.flush()
        await db.refresh(inspection)
        
        logger.info(f"Added {len(photos)} photos to inspection {inspection.business_id}")
        return inspection
    
    @staticmethod
    async def update_inspection(
        db: AsyncSession,
        inspection_id: str,
        **kwargs
    ) -> Optional[Inspection]:
        """
        Update inspection fields.
        
        Args:
            db: Database session
            inspection_id: Inspection UUID
            **kwargs: Fields to update
            
        Returns:
            Updated Inspection object or None if not found
        """
        inspection = await InspectionService.get_by_id(db, inspection_id)
        if not inspection:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(inspection, key) and value is not None:
                setattr(inspection, key, value)
        
        inspection.updated_at = datetime.now(timezone.utc)
        
        await db.flush()
        await db.refresh(inspection)
        
        logger.info(f"Updated inspection {inspection.business_id}")
        return inspection
    
    @staticmethod
    async def add_photo(
        db: AsyncSession,
        inspection_id: str,
        photo_url: str,
        uploaded_by: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        gps: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> Optional[Inspection]:
        """
        Add a single photo to inspection.
        
        Args:
            db: Database session
            inspection_id: Inspection UUID
            photo_url: URL of the photo
            uploaded_by: User who uploaded the photo
            timestamp: When photo was taken
            gps: GPS coordinates dict
            notes: Photo notes/caption
            
        Returns:
            Updated Inspection object or None if not found
        """
        inspection = await InspectionService.get_by_id(db, inspection_id)
        if not inspection:
            return None
        
        photo_data = {
            "url": photo_url,
            "uploaded_by": uploaded_by,
            "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat(),
            "gps": gps,
            "notes": notes
        }
        
        if not inspection.photos:
            inspection.photos = {"items": []}
        elif isinstance(inspection.photos, list):
            inspection.photos = {"items": inspection.photos}
        
        if "items" not in inspection.photos:
            inspection.photos["items"] = []
        
        inspection.photos["items"].append(photo_data)
        inspection.updated_at = datetime.now(timezone.utc)
        
        await db.flush()
        await db.refresh(inspection)
        
        logger.info(f"Added photo to inspection {inspection.business_id}")
        return inspection
    
    @staticmethod
    async def add_deficiency(
        db: AsyncSession,
        inspection_id: str,
        description: str,
        severity: str = "Medium",
        photo_refs: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> Optional[Inspection]:
        """
        Add a deficiency to inspection.
        
        Args:
            db: Database session
            inspection_id: Inspection UUID
            description: Deficiency description
            severity: Severity level (Low, Medium, High, Critical)
            photo_refs: References to photo URLs
            notes: Additional notes
            
        Returns:
            Updated Inspection object or None if not found
        """
        inspection = await InspectionService.get_by_id(db, inspection_id)
        if not inspection:
            return None
        
        deficiency_data = {
            "description": description,
            "severity": severity,
            "photo_refs": photo_refs or [],
            "notes": notes,
            "status": "Open",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        if not inspection.deficiencies:
            inspection.deficiencies = {"items": []}
        elif isinstance(inspection.deficiencies, list):
            inspection.deficiencies = {"items": inspection.deficiencies}
        
        if "items" not in inspection.deficiencies:
            inspection.deficiencies["items"] = []
        
        inspection.deficiencies["items"].append(deficiency_data)
        inspection.updated_at = datetime.now(timezone.utc)
        
        await db.flush()
        await db.refresh(inspection)
        
        logger.info(f"Added deficiency to inspection {inspection.business_id}")
        return inspection
    
    @staticmethod
    async def cancel_inspection(
        db: AsyncSession,
        inspection_id: str
    ) -> Optional[Inspection]:
        """
        Cancel an inspection (soft delete).
        
        Args:
            db: Database session
            inspection_id: Inspection UUID
            
        Returns:
            Updated Inspection object or None if not found
        """
        inspection = await InspectionService.get_by_id(db, inspection_id)
        if not inspection:
            return None
        
        inspection.status = "Cancelled"
        inspection.updated_at = datetime.now(timezone.utc)
        
        await db.flush()
        await db.refresh(inspection)
        
        logger.info(f"Cancelled inspection {inspection.business_id}")
        return inspection
    
    @staticmethod
    async def run_precheck(
        db: AsyncSession,
        inspection_id: str,
        checklist_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Run precheck AI analysis (stub for Phase C).
        
        Args:
            db: Database session
            inspection_id: Inspection UUID
            checklist_items: Items to check
            
        Returns:
            Precheck results (stub implementation)
        """
        inspection = await InspectionService.get_by_id(db, inspection_id)
        if not inspection:
            raise ValueError(f"Inspection not found: {inspection_id}")
        
        # TODO: Implement actual AI precheck logic in Phase C
        logger.info(f"Precheck stub called for inspection {inspection.business_id}")
        
        return {
            "status": "stub",
            "message": "Precheck integration coming in Phase C",
            "inspection_id": inspection_id,
            "business_id": inspection.business_id
        }


# Global service instance
inspection_service = InspectionService()
