from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr
import logging

from app.services.db_service import db_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class ClientCreate(BaseModel):
    """Request model for creating a client."""
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    status: Optional[str] = "Active"
    client_type: Optional[str] = "Residential"


class ClientUpdate(BaseModel):
    """Request model for updating a client."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    status: Optional[str] = None
    client_type: Optional[str] = None


# ==================== ROUTES ====================

@router.get("/")
async def get_all_clients():
async def get_all_clients():
    """
    Get all clients from PostgreSQL database
    """
    try:
        logger.info("Fetching clients from database")
        clients = await db_service.get_clients_data()
        logger.info(f"Retrieved {len(clients)} clients from database")
        
        if clients and len(clients) > 0:
            # Log first client structure to help debug
            first_keys = list(clients[0].keys())
            logger.info(f"First client keys: {first_keys}")
            logger.info(f"First client sample: Client ID={clients[0].get('Client ID', 'N/A')}, Name={clients[0].get('Client Name', clients[0].get('Full Name', 'N/A'))}")
        
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
        
        clients = await db_service.get_clients_data()
        
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
        client = await db_service.get_client_by_id(client_id)
        
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
        updated_client = await db_service.update_client(client_id, updates)
        return updated_client
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update client: {str(e)}")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_client(client_data: ClientCreate):
    """
    Create a new client
    """
    try:
        client_dict = client_data.model_dump(exclude_none=True)
        new_client = await db_service.create_client(client_dict)
        return new_client
        
    except Exception as e:
        logger.error(f"Failed to create client: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create client: {str(e)}")


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: str):
    """
    Delete a client by ID
    """
    try:
        deleted = await db_service.delete_client(client_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
        
        return None  # 204 No Content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete client: {str(e)}")


@router.get("/by-business-id/{business_id}")
async def get_client_by_business_id(business_id: str):
    """
    Get a specific client by business ID (e.g., CL-00001)
    """
    try:
        from app.services.db_service import db_service
        
        client = await db_service.get_client_by_business_id(business_id)
        
        if not client:
            raise HTTPException(status_code=404, detail=f"Client with business ID {business_id} not found")
        
        return client
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get client by business ID {business_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve client: {str(e)}")
