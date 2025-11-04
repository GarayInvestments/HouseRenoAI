from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging
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
        clients = await google_service.get_clients_data()
        logger.info(f"Successfully retrieved {len(clients)} clients")
        return clients
        
    except Exception as e:
        error_msg = f"Failed to get clients: {str(e)}"
        logger.error(error_msg)
        logger.exception(e)  # This will log the full traceback
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
