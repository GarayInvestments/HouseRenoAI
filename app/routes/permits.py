from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from app.services.google_service import google_service
from app.services.openai_service import openai_service

logger = logging.getLogger(__name__)
router = APIRouter()

class PermitUpdate(BaseModel):
    permit_id: str
    updates: Dict[str, Any]
    notify_team: bool = True

class PermitResponse(BaseModel):
    permit_id: str
    data: Dict[str, Any]
    last_updated: str

@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_permits():
    """
    Get all permits from Google Sheets
    """
    try:
        permits = await google_service.get_permits_data()
        logger.info(f"Retrieved {len(permits)} permits")
        return permits
        
    except Exception as e:
        logger.error(f"Failed to get permits: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve permits: {str(e)}")

@router.get("/{permit_id}", response_model=PermitResponse)
async def get_permit(permit_id: str):
    """
    Get a specific permit by ID
    """
    try:
        permits = await google_service.get_permits_data()
        
        # Find permit by ID (assuming there's an ID column)
        permit = None
        for p in permits:
            if p.get('ID') == permit_id or p.get('Permit ID') == permit_id:
                permit = p
                break
        
        if not permit:
            raise HTTPException(status_code=404, detail=f"Permit {permit_id} not found")
        
        return PermitResponse(
            permit_id=permit_id,
            data=permit,
            last_updated=permit.get('Last Updated', 'Unknown')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get permit {permit_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve permit: {str(e)}")

@router.put("/{permit_id}")
async def update_permit(permit_id: str, update_data: PermitUpdate):
    """
    Update a specific permit
    """
    try:
        # Get current permits data
        permits = await google_service.get_permits_data()
        
        # Find the permit to update
        permit_index = None
        for i, p in enumerate(permits):
            if p.get('ID') == permit_id or p.get('Permit ID') == permit_id:
                permit_index = i
                break
        
        if permit_index is None:
            raise HTTPException(status_code=404, detail=f"Permit {permit_id} not found")
        
        # Update the permit data
        updated_permit = permits[permit_index].copy()
        updated_permit.update(update_data.updates)
        updated_permit['Last Updated'] = str(datetime.now())
        
        # Here you would implement the actual sheet update logic
        # This is a simplified example - you'd need to map back to sheet rows/columns
        
        # Send notification if requested
        if update_data.notify_team:
            message = f"Permit {permit_id} has been updated with: {', '.join(update_data.updates.keys())}"
            await google_service.notify_chat(message)
        
        logger.info(f"Updated permit {permit_id}")
        return {"status": "success", "message": f"Permit {permit_id} updated successfully"}
        
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
        permits = await google_service.get_permits_data()
        
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
        permits = await google_service.get_permits_data()
        
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

# Add missing import
from datetime import datetime