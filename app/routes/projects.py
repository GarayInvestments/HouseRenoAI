from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

import app.services.google_service as google_service_module

logger = logging.getLogger(__name__)
router = APIRouter()

def get_google_service():
    """Helper function to get Google service with proper error handling"""
    if not hasattr(google_service_module, 'google_service') or google_service_module.google_service is None:
        raise HTTPException(status_code=503, detail="Google service not initialized")
    return google_service_module.google_service

@router.get("/")
async def get_all_projects():
    """
    Get all projects from Google Sheets
    """
    try:
        google_service = get_google_service()
        projects = await google_service.get_projects_data()
        logger.info(f"Retrieved {len(projects)} projects")
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
        google_service = get_google_service()
        projects = await google_service.get_projects_data()
        
        # Find project by ID
        project = None
        for p in projects:
            if p.get('Project ID') == project_id:
                project = p
                break
        
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
async def update_project(project_id: str, update_data: Dict[str, Any]):
    """
    Update a specific project in Google Sheets
    """
    try:
        updates = update_data.get("updates", {})
        notify_team = update_data.get("notify_team", True)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        google_service = get_google_service()
        
        # Verify project exists first
        projects = await google_service.get_projects_data()
        project = None
        for p in projects:
            if p.get('Project ID') == project_id:
                project = p
                break
        
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        # Update the project in Google Sheets
        success = await google_service.update_record_by_id(
            sheet_name='Projects',
            id_field='Project ID',
            record_id=project_id,
            updates=updates
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update project in Google Sheets")
        
        # Send notification if requested
        if notify_team:
            project_name = project.get('Project Name', project_id)
            message = f"✅ Project '{project_name}' updated: {', '.join([f'{k}={v}' for k, v in updates.items()])}"
            await google_service.notify_chat(message)
        
        logger.info(f"Successfully updated project {project_id} in Google Sheets")
        return {
            "status": "success", 
            "message": f"Project {project_id} updated successfully",
            "updated_fields": list(updates.keys()),
            "project_name": project.get('Project Name', project_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")

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
        google_service = get_google_service()
        projects = await google_service.get_projects_data()
        
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
