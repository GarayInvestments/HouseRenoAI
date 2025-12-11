"""
Permit Service - Business logic for permit management.

Handles permit CRUD operations, status tracking, and relationship management.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import logging

from app.db.models import Permit, Project

logger = logging.getLogger(__name__)


class PermitService:
    """Service for managing permits and their lifecycle."""
    
    @staticmethod
    async def get_permits(
        db: AsyncSession,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Permit]:
        """
        Get permits with optional filtering.
        
        Args:
            db: Database session
            project_id: Filter by project UUID
            status: Filter by permit status
            skip: Number of records to skip (pagination)
            limit: Maximum records to return
            
        Returns:
            List of Permit objects
        """
        query = select(Permit).order_by(Permit.created_at.desc())
        
        if project_id:
            query = query.where(Permit.project_id == project_id)
        if status:
            query = query.where(Permit.status == status)
            
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        permits = result.scalars().all()
        
        logger.info(f"Retrieved {len(permits)} permits (project_id={project_id}, status={status})")
        return permits
    
    @staticmethod
    async def get_by_id(db: AsyncSession, permit_id: str) -> Optional[Permit]:
        """
        Get permit by UUID.
        
        Args:
            db: Database session
            permit_id: Permit UUID
            
        Returns:
            Permit object or None if not found
        """
        result = await db.execute(
            select(Permit).where(Permit.permit_id == permit_id)
        )
        permit = result.scalar_one_or_none()
        
        if permit:
            logger.info(f"Found permit {permit.business_id} (UUID: {permit_id})")
        else:
            logger.warning(f"Permit not found: {permit_id}")
            
        return permit
    
    @staticmethod
    async def get_by_business_id(db: AsyncSession, business_id: str) -> Optional[Permit]:
        """
        Get permit by business ID (e.g., PER-00001).
        
        Args:
            db: Database session
            business_id: Business ID (PER-XXXXX)
            
        Returns:
            Permit object or None if not found
        """
        result = await db.execute(
            select(Permit).where(Permit.business_id == business_id)
        )
        permit = result.scalar_one_or_none()
        
        if permit:
            logger.info(f"Found permit {business_id} (UUID: {permit.permit_id})")
        else:
            logger.warning(f"Permit not found: {business_id}")
            
        return permit
    
    @staticmethod
    async def create_permit(
        db: AsyncSession,
        project_id: str,
        permit_type: str,
        permit_number: Optional[str] = None,
        status: str = "Pending",
        application_date: Optional[datetime] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> Permit:
        """
        Create a new permit.
        
        Args:
            db: Database session
            project_id: Project UUID
            permit_type: Type of permit (e.g., "Building", "Electrical")
            permit_number: External permit number from jurisdiction
            status: Initial status (default: "Pending")
            application_date: When permit was applied for
            extra: Additional metadata
            
        Returns:
            Created Permit object with auto-generated business_id
        """
        # Verify project exists
        project_result = await db.execute(
            select(Project).where(Project.project_id == project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        permit = Permit(
            project_id=project_id,
            permit_type=permit_type,
            permit_number=permit_number,
            status=status,
            application_date=application_date or datetime.now(timezone.utc),
            extra=extra or {}
        )
        
        db.add(permit)
        await db.flush()  # Get business_id from trigger
        await db.refresh(permit)
        
        logger.info(f"Created permit {permit.business_id} for project {project.business_id}")
        return permit
    
    @staticmethod
    async def update_status(
        db: AsyncSession,
        permit_id: str,
        new_status: str,
        notes: Optional[str] = None
    ) -> Optional[Permit]:
        """
        Update permit status with event tracking.
        
        Args:
            db: Database session
            permit_id: Permit UUID
            new_status: New status value
            notes: Optional notes about status change
            
        Returns:
            Updated Permit object or None if not found
        """
        permit = await PermitService.get_by_id(db, permit_id)
        if not permit:
            return None
        
        old_status = permit.status
        permit.status = new_status
        permit.updated_at = datetime.now(timezone.utc)
        
        # Track status change in history
        if not permit.status_history:
            permit.status_history = []
        
        permit.status_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "old_status": old_status,
            "new_status": new_status,
            "notes": notes
        })
        
        await db.flush()
        await db.refresh(permit)
        
        logger.info(f"Updated permit {permit.business_id} status: {old_status} → {new_status}")
        return permit
    
    @staticmethod
    async def set_approval(
        db: AsyncSession,
        permit_id: str,
        approval_date: datetime,
        approved_by: Optional[str] = None
    ) -> Optional[Permit]:
        """
        Set permit approval details.
        
        Args:
            db: Database session
            permit_id: Permit UUID
            approval_date: When permit was approved
            approved_by: Who approved the permit
            
        Returns:
            Updated Permit object or None if not found
        """
        permit = await PermitService.get_by_id(db, permit_id)
        if not permit:
            return None
        
        permit.approval_date = approval_date
        permit.status = "Approved"
        permit.updated_at = datetime.now(timezone.utc)
        
        if approved_by:
            if not permit.extra:
                permit.extra = {}
            permit.extra["approved_by"] = approved_by
        
        await db.flush()
        await db.refresh(permit)
        
        logger.info(f"Approved permit {permit.business_id} on {approval_date}")
        return permit


# Global service instance
permit_service = PermitService()
