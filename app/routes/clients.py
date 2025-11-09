from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
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
            logger.info("Attempting to fetch clients from Clients sheet")
            clients = await google_service.get_clients_data()
            logger.info(f"Retrieved {len(clients)} clients from get_clients_data()")
            
            if clients and len(clients) > 0:
                # Log first client structure to help debug
                if clients:
                    first_keys = list(clients[0].keys())
                    logger.info(f"First client keys: {first_keys}")
                    logger.info(f"First client sample: Client ID={clients[0].get('Client ID', 'N/A')}, Name={clients[0].get('Client Name', clients[0].get('Full Name', 'N/A'))}")
                
                logger.info(f"Successfully retrieved {len(clients)} clients from Clients sheet")
                return clients
        except Exception as sheet_error:
            logger.warning(f"Could not read Clients sheet: {sheet_error}", exc_info=True)
        
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

@router.get("/lookup")
async def lookup_client(
    name: Optional[str] = Query(None, description="Client name to search for"),
    email: Optional[str] = Query(None, description="Client email to search for")
):
    """
    Lookup client by name or email (fuzzy matching)
    Returns best match with confidence score
    """
    try:
        if not name and not email:
            raise HTTPException(status_code=400, detail="Must provide name or email parameter")
        
        google_service = get_google_service()
        clients = await google_service.get_clients_data()
        
        best_match = None
        best_score = 0
        
        for client in clients:
            score = 0
            matches = []
            
            # Try multiple field name variations
            client_name = (
                client.get('Full Name') or 
                client.get('Client Name') or 
                client.get('Name') or 
                ''
            ).strip().lower()
            
            client_email = (
                client.get('Email') or 
                client.get('Client Email') or 
                ''
            ).strip().lower()
            
            client_company = (
                client.get('Company') or 
                client.get('Client Company') or 
                ''
            ).strip().lower()
            
            # Name matching (if provided)
            if name:
                search_name = name.strip().lower()
                
                # Exact match
                if search_name == client_name:
                    score += 100
                    matches.append("exact_name")
                # Contains match
                elif search_name in client_name or client_name in search_name:
                    score += 70
                    matches.append("partial_name")
                # Check if name matches company
                elif search_name in client_company or client_company in search_name:
                    score += 50
                    matches.append("company_name")
                # Word overlap (e.g., "Ajay R Nair" vs "Ajay Nair")
                else:
                    name_words = set(search_name.split())
                    client_words = set(client_name.split())
                    overlap = len(name_words & client_words)
                    if overlap > 0:
                        score += overlap * 30
                        matches.append("word_overlap")
            
            # Email matching (if provided)
            if email:
                search_email = email.strip().lower()
                
                # Exact match
                if search_email == client_email:
                    score += 100
                    matches.append("exact_email")
                # Domain match
                elif search_email and client_email and search_email.split('@')[-1] == client_email.split('@')[-1]:
                    score += 40
                    matches.append("email_domain")
            
            # Update best match if this is better
            if score > best_score:
                best_score = score
                best_match = {
                    'client': client,
                    'confidence': min(100, score),  # Cap at 100
                    'matches': matches,
                    'client_id': client.get('Client ID') or client.get('ID'),
                    'full_name': client.get('Full Name') or client.get('Client Name') or client.get('Name'),
                    'email': client.get('Email') or client.get('Client Email'),
                    'company': client.get('Company') or client.get('Client Company'),
                    'phone': client.get('Phone') or client.get('Client Phone')
                }
        
        # Return best match if confidence is reasonable (>30)
        if best_match and best_match['confidence'] > 30:
            logger.info(f"Found client match: {best_match['full_name']} (confidence: {best_match['confidence']})")
            return best_match
        else:
            # No good match found
            return {
                'client': None,
                'confidence': 0,
                'matches': [],
                'message': 'No matching client found'
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to lookup client: {e}")
        raise HTTPException(status_code=500, detail=f"Client lookup failed: {str(e)}")

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

@router.put("/{client_id}")
async def update_client(client_id: str, updates: Dict[str, Any]):
    """
    Update a specific client by ID
    """
    try:
        google_service = get_google_service()
        
        # Verify client exists first
        clients = await google_service.get_clients_data()
        client = None
        for c in clients:
            if c.get('Client ID') == client_id or c.get('ID') == client_id:
                client = c
                break
        
        if not client:
            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
        
        # Update the client in Google Sheets
        success = await google_service.update_record_by_id(
            sheet_name='Clients',
            id_field='Client ID',
            record_id=client_id,
            updates=updates
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update client in Google Sheets")
        
        # Return updated client data
        updated_clients = await google_service.get_clients_data()
        for c in updated_clients:
            if c.get('Client ID') == client_id or c.get('ID') == client_id:
                return {
                    'success': True,
                    'message': f'Client {client_id} updated successfully',
                    'client': c
                }
        
        return {
            'success': True,
            'message': f'Client {client_id} updated successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update client: {str(e)}")
