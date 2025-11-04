from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

import app.services.google_service as google_service_module
from app.services.openai_service import openai_service

logger = logging.getLogger(__name__)
router = APIRouter()

def get_google_service():
    """Helper function to get Google service with proper error handling"""
    if not hasattr(google_service_module, 'google_service') or google_service_module.google_service is None:
        raise HTTPException(status_code=503, detail="Google service not initialized")
    return google_service_module.google_service

@router.get("/")
async def get_all_permits():
    """
    Get all permits from Google Sheets
    """
    try:
        google_service = get_google_service()
        permits = await google_service.get_permits_data()
        logger.info(f"Retrieved {len(permits)} permits")
        return permits
        
    except Exception as e:
        logger.error(f"Failed to get permits: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve permits: {str(e)}")

@router.get("/{permit_id}")
async def get_permit(permit_id: str):
    """
    Get a specific permit by ID
    """
    try:
        google_service = get_google_service(); permits = await google_service.get_permits_data()
        
        # Find permit by ID (assuming there's an ID column)
        permit = None
        for p in permits:
            if p.get('ID') == permit_id or p.get('Permit ID') == permit_id:
                permit = p
                break
        
        if not permit:
            raise HTTPException(status_code=404, detail=f"Permit {permit_id} not found")
        
        return {
            "permit_id": permit_id,
            "data": permit,
            "last_updated": permit.get('Last Updated', 'Unknown')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get permit {permit_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve permit: {str(e)}")

@router.put("/{permit_id}")
async def update_permit(permit_id: str, update_data: Dict[str, Any]):
    """
    Update a specific permit in Google Sheets
    """
    try:
        updates = update_data.get("updates", {})
        notify_team = update_data.get("notify_team", True)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        google_service = get_google_service()
        
        # Verify permit exists first
        permits = await google_service.get_permits_data()
        permit_exists = any(
            p.get('ID') == permit_id or p.get('Permit ID') == permit_id 
            for p in permits
        )
        
        if not permit_exists:
            raise HTTPException(status_code=404, detail=f"Permit {permit_id} not found")
        
        # Update the permit in Google Sheets
        success = await google_service.update_record_by_id(
            sheet_name='Permits',
            id_field='Permit ID',
            record_id=permit_id,
            updates=updates
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update permit in Google Sheets")
        
        # Send notification if requested
        if notify_team:
            message = f"✅ Permit {permit_id} updated: {', '.join([f'{k}={v}' for k, v in updates.items()])}"
            await google_service.notify_chat(message)
        
        logger.info(f"Successfully updated permit {permit_id} in Google Sheets")
        return {
            "status": "success", 
            "message": f"Permit {permit_id} updated successfully",
            "updated_fields": list(updates.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update permit {permit_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update permit: {str(e)}")

@router.get("/search/")
async def search_permits(
    query: str = Query(..., description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    project_id: Optional[str] = Query(None, description="Filter by project ID")
):
    """
    Search permits with various filters
    """
    try:
        google_service = get_google_service(); permits = await google_service.get_permits_data()
        
        # Apply filters
        filtered_permits = permits
        
        if status:
            filtered_permits = [p for p in filtered_permits if p.get('Status', '').lower() == status.lower()]
        
        if project_id:
            filtered_permits = [p for p in filtered_permits if p.get('Project ID') == project_id]
        
        # Use AI to search through permits based on natural language query
        if query and query.lower() != 'all':
            # Use OpenAI to analyze which permits match the query
            search_context = {
                'permits': filtered_permits[:10],  # Limit for token efficiency
                'query': query
            }
            
            ai_analysis = await openai_service.process_chat_message(
                f"Find permits that match this query: {query}. Return only the permit IDs that match.",
                search_context
            )
            
            # This is simplified - you'd implement better matching logic
            logger.info(f"AI search analysis: {ai_analysis}")
        
        logger.info(f"Found {len(filtered_permits)} permits matching criteria")
        return filtered_permits
        
    except Exception as e:
        logger.error(f"Failed to search permits: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/analyze")
async def analyze_permits():
    """
    Generate AI analysis of all permits
    """
    try:
        google_service = get_google_service(); permits = await google_service.get_permits_data()
        
        if not permits:
            return {"analysis": "No permits found to analyze"}
        
        # Use OpenAI to analyze permit data
        analysis = await openai_service.analyze_permit_data({
            'total_permits': len(permits),
            'permits_sample': permits[:5],  # Send sample for analysis
            'analysis_type': 'overview'
        })
        
        return {
            "total_permits": len(permits),
            "analysis": analysis,
            "generated_at": str(datetime.now())
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze permits: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
