from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
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
async def get_all_clients():
    """
    Get all clients from Google Sheets
    """
    try:
        google_service = get_google_service()
        
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
        logger.error(f"Failed to get clients: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve clients: {str(e)}")

@router.get("/{client_id}")
async def get_client(client_id: str):
    """
    Get a specific client by ID
    """
    try:
        google_service = get_google_service()
        clients = await google_service.get_clients_data()
        
        # Find client by ID - try both 'Client ID' and 'ID' fields
        client = None
        for c in clients:
            if c.get('Client ID') == client_id or c.get('ID') == client_id:
                client = c
                break
        
        if not client:
            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
        
        # Return the client data directly (not wrapped in an object)
        return client
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve client: {str(e)}")
