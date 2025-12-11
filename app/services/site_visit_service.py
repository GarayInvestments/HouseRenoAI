"""
Site Visit Service - Business logic for site visit management.

Handles site visit scheduling, execution, photo uploads, and follow-up action creation.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import logging

from app.db.models import SiteVisit, Project

logger = logging.getLogger(__name__)


class SiteVisitService:
    """Service for managing site visits and follow-up actions."""
    
    @staticmethod
    async def get_site_visits(
        db: AsyncSession,
        project_id: Optional[str] = None,
        client_id: Optional[str] = None,
        status: Optional[str] = None,
        visit_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SiteVisit]:
        """
        Get site visits with optional filtering.
        
        Args:
            db: Database session
            project_id: Filter by project UUID
            client_id: Filter by client UUID
            status: Filter by visit status
            visit_type: Filter by visit type
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of SiteVisit objects
        """
        query = select(SiteVisit).order_by(SiteVisit.scheduled_date.desc())
        
        if project_id:
            query = query.where(SiteVisit.project_id == project_id)
        if client_id:
            query = query.where(SiteVisit.client_id == client_id)
        if status:
            query = query.where(SiteVisit.status == status)
        if visit_type:
            query = query.where(SiteVisit.visit_type == visit_type)
            
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        visits = result.scalars().all()
        
        logger.info(f"Retrieved {len(visits)} site visits")
        return visits
    
    @staticmethod
    async def get_by_id(db: AsyncSession, visit_id: str) -> Optional[SiteVisit]:
        """Get site visit by UUID."""
        result = await db.execute(
            select(SiteVisit).where(SiteVisit.visit_id == visit_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_business_id(db: AsyncSession, business_id: str) -> Optional[SiteVisit]:
        """Get site visit by business ID (e.g., SV-00001)."""
        result = await db.execute(
            select(SiteVisit).where(SiteVisit.business_id == business_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def schedule_visit(
        db: AsyncSession,
        project_id: str,
        client_id: str,
        visit_type: str,
        scheduled_date: datetime,
        attendees: Optional[List[str]] = None,
        notes: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> SiteVisit:
        """
        Schedule a new site visit.
        
        Args:
            db: Database session
            project_id: Project UUID
            client_id: Client UUID
            visit_type: Type of visit (e.g., "Initial Consultation", "Progress Check")
            scheduled_date: When visit is scheduled
            attendees: List of attendee names
            notes: Purpose/notes for visit
            extra: Additional metadata
            
        Returns:
            Created SiteVisit object with auto-generated business_id
        """
        # Verify project exists
        project_result = await db.execute(
            select(Project).where(Project.project_id == project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        visit = SiteVisit(
            project_id=project_id,
            client_id=client_id,
            visit_type=visit_type,
            scheduled_date=scheduled_date,
            status="Scheduled",
            attendees=attendees or [],
            notes=notes,
            extra=extra or {}
        )
        
        db.add(visit)
        await db.flush()
        await db.refresh(visit)
        
        logger.info(f"Scheduled site visit {visit.business_id} for project {project.business_id}")
        return visit
    
    @staticmethod
    async def start_visit(
        db: AsyncSession,
        visit_id: str,
        actual_start_time: Optional[datetime] = None,
        gps_location: Optional[Dict[str, float]] = None
    ) -> Optional[SiteVisit]:
        """
        Mark visit as in progress.
        
        Args:
            db: Database session
            visit_id: Site visit UUID
            actual_start_time: When visit actually started
            gps_location: GPS coordinates {"latitude": x, "longitude": y}
            
        Returns:
            Updated SiteVisit object or None if not found
        """
        visit = await SiteVisitService.get_by_id(db, visit_id)
        if not visit:
            return None
        
        visit.status = "In Progress"
        visit.start_time = actual_start_time or datetime.now(timezone.utc)
        
        if gps_location:
            # Convert dict to "lat,lon" string format
            visit.gps_location = f"{gps_location['latitude']},{gps_location['longitude']}"
        
        visit.updated_at = datetime.now(timezone.utc)
        
        await db.flush()
        await db.refresh(visit)
        
        logger.info(f"Started site visit {visit.business_id}")
        return visit
    
    @staticmethod
    async def complete_visit(
        db: AsyncSession,
        visit_id: str,
        actual_end_time: Optional[datetime] = None,
        summary: Optional[str] = None,
        deficiencies: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[SiteVisit]:
        """
        Mark visit as complete with summary.
        
        Args:
            db: Database session
            visit_id: Site visit UUID
            actual_end_time: When visit ended
            summary: Visit summary
            deficiencies: List of deficiencies found
            
        Returns:
            Updated SiteVisit object or None if not found
        """
        visit = await SiteVisitService.get_by_id(db, visit_id)
        if not visit:
            return None
        
        visit.status = "Completed"
        visit.end_time = actual_end_time or datetime.now(timezone.utc)
        visit.notes = summary
        
        if deficiencies:
            visit.deficiencies = deficiencies
        
        visit.updated_at = datetime.now(timezone.utc)
        
        await db.flush()
        await db.refresh(visit)
        
        logger.info(f"Completed site visit {visit.business_id}")
        return visit
    
    @staticmethod
    async def upload_photos(
        db: AsyncSession,
        visit_id: str,
        photos: List[Dict[str, Any]]
    ) -> Optional[SiteVisit]:
        """
        Add photos to site visit.
        
        Args:
            db: Database session
            visit_id: Site visit UUID
            photos: List of photo metadata dicts with keys:
                    - url: Photo URL
                    - caption: Optional caption
                    - timestamp: When photo was taken
                    - location: Optional GPS coordinates
            
        Returns:
            Updated SiteVisit object or None if not found
        """
        visit = await SiteVisitService.get_by_id(db, visit_id)
        if not visit:
            return None
        
        # JSONB field - ensure it's an array
        current_photos = visit.photos if visit.photos and isinstance(visit.photos, list) else []
        
        # Add timestamp to photos if not present
        for photo in photos:
            if "timestamp" not in photo:
                photo["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Update JSONB field with combined array
        visit.photos = current_photos + photos
        visit.updated_at = datetime.now(timezone.utc)
        
        await db.flush()
        await db.refresh(visit)
        
        logger.info(f"Added {len(photos)} photos to site visit {visit.business_id}")
        return visit
    
    @staticmethod
    async def create_follow_up_actions(
        db: AsyncSession,
        visit_id: str,
        actions: List[Dict[str, Any]]
    ) -> Optional[SiteVisit]:
        """
        Create follow-up actions from site visit.
        
        Args:
            db: Database session
            visit_id: Site visit UUID
            actions: List of follow-up action dicts with keys:
                     - description: Action description
                     - priority: Priority level (high/medium/low)
                     - assigned_to: Who is responsible
                     - due_date: When action should be completed
                     - status: Action status (default: "pending")
            
        Returns:
            Updated SiteVisit object or None if not found
        """
        visit = await SiteVisitService.get_by_id(db, visit_id)
        if not visit:
            return None
        
        # JSONB field - ensure it's an array
        current_actions = visit.follow_up_actions if visit.follow_up_actions and isinstance(visit.follow_up_actions, list) else []
        
        # Add creation timestamp and default status to actions
        for action in actions:
            if "created_at" not in action:
                action["created_at"] = datetime.now(timezone.utc).isoformat()
            if "status" not in action:
                action["status"] = "pending"
        
        # Update JSONB field with combined array
        visit.follow_up_actions = current_actions + actions
        visit.updated_at = datetime.now(timezone.utc)
        
        await db.flush()
        await db.refresh(visit)
        
        logger.info(f"Created {len(actions)} follow-up actions for site visit {visit.business_id}")
        return visit


# Global service instance
site_visit_service = SiteVisitService()
