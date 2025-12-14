"""
API routes for site visit management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from app.services.db_service import db_service
from app.routes.auth_supabase import get_current_user
from app.db.models import User

logger = logging.getLogger(__name__)
router = APIRouter()


class SiteVisitCreate(BaseModel):
    project_id: str
    client_id: Optional[str] = None
    visit_type: Optional[str] = None
    status: Optional[str] = "scheduled"
    scheduled_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attendees: Optional[list] = None
    gps_location: Optional[str] = None
    photos: Optional[list] = None
    notes: Optional[str] = None
    weather: Optional[str] = None
    deficiencies: Optional[list] = None
    follow_up_actions: Optional[list] = None


class SiteVisitUpdate(BaseModel):
    client_id: Optional[str] = None
    visit_type: Optional[str] = None
    status: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attendees: Optional[list] = None
    gps_location: Optional[str] = None
    photos: Optional[list] = None
    notes: Optional[str] = None
    weather: Optional[str] = None
    deficiencies: Optional[list] = None
    follow_up_actions: Optional[list] = None


@router.get("/")
async def get_all_site_visits(current_user: User = Depends(get_current_user)):
    """Get all site visits"""
    try:
        logger.info(f"Fetching all site visits for user {current_user.email}")
        visits = await db_service.get_site_visits_data()
        logger.info(f"Retrieved {len(visits) if isinstance(visits, list) else 'unknown'} site visits")
        return visits
    except Exception as e:
        logger.error(f"Failed to get site visits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{visit_id}")
async def get_site_visit(visit_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific site visit"""
    try:
        visit = await db_service.get_site_visit_by_id(visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail=f"Site visit {visit_id} not found")
        return visit
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_site_visit(visit_data: SiteVisitCreate, current_user: User = Depends(get_current_user)):
    """Create a new site visit"""
    try:
        visit_dict = visit_data.model_dump(exclude_none=True)
        new_visit = await db_service.create_site_visit(visit_dict)
        return new_visit
    except Exception as e:
        logger.error(f"Failed to create site visit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{visit_id}")
async def update_site_visit(visit_id: str, visit_data: SiteVisitUpdate, current_user: User = Depends(get_current_user)):
    """Update a site visit"""
    try:
        update_dict = visit_data.model_dump(exclude_none=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        updated_visit = await db_service.update_site_visit(visit_id, update_dict)
        return updated_visit
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site_visit(visit_id: str, current_user: User = Depends(get_current_user)):
    """Delete a site visit"""
    try:
        deleted = await db_service.delete_site_visit(visit_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Site visit {visit_id} not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/{project_id}")
async def get_site_visits_by_project(project_id: str):
    """Get all site visits for a specific project"""
    try:
        visits = await db_service.get_site_visits_by_project(project_id)
        return visits
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
