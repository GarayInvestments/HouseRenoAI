from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from app.services.db_service import db_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class ProjectCreate(BaseModel):
    """Request model for creating a project."""
    client_id: str
    project_name: str
    project_address: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    status: Optional[str] = "Planning"
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    target_completion: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    """Request model for updating a project."""
    client_id: Optional[str] = None
    project_name: Optional[str] = None
    project_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    target_completion: Optional[datetime] = None


# ==================== ROUTES ====================

@router.get("/")
async def get_all_projects():
    """
    Get all projects from PostgreSQL database
    """
    try:
        projects = await db_service.get_projects_data()
        logger.info(f"Retrieved {len(projects)} projects from database")
        return projects
        
    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve projects: {str(e)}")

@router.get("/{project_id}")
async def get_project(project_id: str):
    """
    Get a specific project by ID
    """
    try:
        project = await db_service.get_project_by_id(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        return {
            "project_id": project_id,
            "data": project,
            "last_updated": project.get('Last Updated', 'Unknown')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve project: {str(e)}")

@router.put("/{project_id}")
async def update_project(project_id: str, project_data: ProjectUpdate):
    """
    Update a specific project
    """
    try:
        update_dict = project_data.model_dump(exclude_none=True)
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        updated_project = await db_service.update_project(project_id, update_dict)
        return updated_project
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_project(project_data: ProjectCreate):
    """
    Create a new project
    """
    try:
        project_dict = project_data.model_dump(exclude_none=True)
        new_project = await db_service.create_project(project_dict)
        return new_project
        
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str):
    """
    Delete a project by ID
    """
    try:
        deleted = await db_service.delete_project(project_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        return None  # 204 No Content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")


@router.get("/search/")
async def search_projects(
    query: str = Query(..., description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    client_id: Optional[str] = Query(None, description="Filter by client ID")
):
    """
    Search projects with various filters
    """
    try:
        projects = await db_service.get_projects_data()
        
        # Apply filters
        filtered_projects = projects
        
        if status:
            filtered_projects = [p for p in filtered_projects if p.get('Status', '').lower() == status.lower()]
        
        if client_id:
            filtered_projects = [p for p in filtered_projects if p.get('Client ID') == client_id]
        
        logger.info(f"Found {len(filtered_projects)} projects matching criteria")
        return filtered_projects
        
    except Exception as e:
        logger.error(f"Failed to search projects: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/by-business-id/{business_id}")
async def get_project_by_business_id(business_id: str):
    """
    Get a specific project by business ID (e.g., PRJ-00001)
    """
    try:
        from app.services.db_service import db_service
        
        project = await db_service.get_project_by_business_id(business_id)
        
        if not project:
            raise HTTPException(status_code=404, detail=f"Project with business ID {business_id} not found")
        
        return {
            "business_id": business_id,
            "data": project
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project by business ID {business_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve project: {str(e)}")
