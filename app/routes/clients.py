from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging
import traceback
from app.services.google_service import google_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_clients():
    """Get all clients from Google Sheets"""
    try:
        if not google_service:
            logger.error("Google service not initialized")
            raise HTTPException(status_code=500, detail="Google service not initialized")
        
        logger.info("Attempting to fetch clients data from Google Sheets")
        
        # Try to get clients data from the Clients sheet
        try:
            clients = await google_service.get_clients_data()
            if clients and len(clients) > 0:
                logger.info(f"Successfully retrieved {len(clients)} clients from Clients sheet")
                return clients
        except Exception as sheet_error:
            logger.warning(f"Could not read Clients sheet: {sheet_error}")
        
        # Fallback: If Clients sheet doesn't exist or is empty, derive from Projects
        logger.info("Falling back to deriving clients from Projects data")
        projects = await google_service.get_projects_data()
        
        # Extract unique clients from projects
        clients_dict = {}
        for project in projects:
            client_id = project.get('Client ID', '')
            if client_id and client_id not in clients_dict:
                clients_dict[client_id] = {
                    'Client ID': client_id,
                    'Client Name': project.get('Owner Name (PM\'s Client)', 'Unknown Client'),
                    'Active Projects': '1',
                    'Email': '',
                    'Phone': '',
                    'Address': '',
                    'City': '',
                    'State': '',
                    'Notes': f'Derived from project: {project.get("Project Name", "")}'
                }
            elif client_id and client_id in clients_dict:
                # Increment project count
                current_count = int(clients_dict[client_id].get('Active Projects', '0'))
                clients_dict[client_id]['Active Projects'] = str(current_count + 1)
        
        clients = list(clients_dict.values())
        logger.info(f"Derived {len(clients)} clients from projects data")
        return clients
        
    except Exception as e:
        error_type = type(e).__name__
        error_str = str(e) if str(e) else f"No error message - {error_type}"
        error_trace = traceback.format_exc()
        error_msg = f"Failed to get clients: {error_str}"
        logger.error(f"{error_msg}\nTraceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/{client_id}", response_model=Dict[str, Any])
async def get_client(client_id: str):
    """Get a specific client by ID"""
    try:
        if not google_service:
            raise HTTPException(status_code=500, detail="Google service not initialized")
        
        clients = await google_service.get_clients_data()
        
        # Find client by ID - try both 'Client ID' and 'ID' fields
        client = None
        for c in clients:
            if c.get('Client ID') == client_id or c.get('ID') == client_id:
                client = c
                break
        
        if not client:
            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
        
        logger.info(f"Retrieved client: {client_id}")
        return client
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
