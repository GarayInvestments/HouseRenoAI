from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging

from app.services.openai_service import openai_service
from app.services.google_service import google_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/")
async def process_chat_message(chat_data: Dict[str, Any]):
    """
    Process a chat message using OpenAI and perform any necessary actions
    """
    try:
        message = chat_data.get("message", "")
        context = chat_data.get("context", {})
        
        logger.info(f"Processing chat message: {message[:100]}...")
        
        # Check if message requires data lookup
        if any(keyword in message.lower() for keyword in ['permit', 'project', 'client', 'status']):
            try:
                permits = await google_service.get_permits_data()
                projects = await google_service.get_projects_data()
                clients = await google_service.get_clients_data()
                
                context.update({
                    'permits_count': len(permits),
                    'projects_count': len(projects),
                    'clients_count': len(clients),
                    'recent_permits': permits[:5] if permits else [],
                    'recent_projects': projects[:5] if projects else []
                })
            except Exception as e:
                logger.warning(f"Could not fetch data context: {e}")
        
        # Process message with OpenAI
        ai_response = await openai_service.process_chat_message(message, context)
        
        # Check if AI response indicates an action should be taken
        action_taken = None
        data_updated = False
        
        # Simple action detection (can be enhanced with function calling)
        if 'update' in message.lower() or 'change' in message.lower():
            action_taken = "Data update request detected"
            # Here you would implement actual data update logic
        
        return {
            "response": ai_response,
            "action_taken": action_taken,
            "data_updated": data_updated
        }
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.get("/status")
async def get_chat_status():
    """
    Get the current status of the chat system
    """
    try:
        # Test OpenAI connection
        openai_status = "connected"
        try:
            await openai_service.process_chat_message("test")
        except:
            openai_status = "error"
        
        # Test Google Sheets connection
        sheets_status = "connected"
        try:
            await google_service.read_sheet_data("A1:A1")
        except:
            sheets_status = "error"
        
        return {
            "status": "operational",
            "openai_status": openai_status,
            "sheets_status": sheets_status,
            "features": [
                "Natural language queries",
                "Permit data access",
                "Project tracking",
                "Automated notifications"
            ]
        }
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")