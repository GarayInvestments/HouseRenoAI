"""
API routes for site visit management.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from app.services.db_service import db_service

logger = logging.getLogger(__name__)
router = APIRouter()


class SiteVisitCreate(BaseModel):
    project_id: str
    visit_date: datetime
    purpose: str
    attendees: Optional[str] = None
    observations: Optional[str] = None
    action_items: Optional[str] = None


class SiteVisitUpdate(BaseModel):
    visit_date: Optional[datetime] = None
    purpose: Optional[str] = None
    attendees: Optional[str] = None
    observations: Optional[str] = None
    action_items: Optional[str] = None


@router.get("/")
async def get_all_site_visits():
    """Get all site visits"""
    try:
        visits = await db_service.get_site_visits_data()
        return visits
    except Exception as e:
        logger.error(f"Failed to get site visits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{visit_id}")
async def get_site_visit(visit_id: str):
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
async def create_site_visit(visit_data: SiteVisitCreate):
    """Create a new site visit"""
    try:
        visit_dict = visit_data.model_dump(exclude_none=True)
        new_visit = await db_service.create_site_visit(visit_dict)
        return new_visit
    except Exception as e:
        logger.error(f"Failed to create site visit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{visit_id}")
async def update_site_visit(visit_id: str, visit_data: SiteVisitUpdate):
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
async def delete_site_visit(visit_id: str):
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
