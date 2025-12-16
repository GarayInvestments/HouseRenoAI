"""
Oversight Actions API routes.
Phase Q.3: API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy import text, select
from datetime import datetime

from app.db.session import AsyncSessionLocal
from app.services.db_service import db_service
from app.routes.auth_supabase import get_current_user
from app.db.models import User, OversightAction
from app.routes.oversight_actions_pydantic import (
    OversightActionCreate,
    OversightActionUpdate
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_oversight_actions(
    project_id: Optional[str] = None,
    qualifier_id: Optional[str] = None,
    licensed_business_id: Optional[str] = None,
    action_type: Optional[str] = None
):
    """
    Get oversight actions with optional filters.
    Returns list of oversight actions matching criteria.
    """
    try:
        async with AsyncSessionLocal() as session:
            # Build dynamic query based on filters
            where_clauses = []
            params = {}
            
            if project_id:
                where_clauses.append("project_id::text = :project_id")
                params["project_id"] = project_id
            
            if qualifier_id:
                where_clauses.append("qualifier_id::text = :qualifier_id")
                params["qualifier_id"] = qualifier_id
            
            if licensed_business_id:
                where_clauses.append("licensed_business_id::text = :licensed_business_id")
                params["licensed_business_id"] = licensed_business_id
            
            if action_type:
                where_clauses.append("action_type = :action_type")
                params["action_type"] = action_type
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            query = f"""
                SELECT 
                    id,
                    action_id,
                    project_id,
                    licensed_business_id,
                    qualifier_id,
                    licensed_business_qualifier_id,
                    action_type,
                    action_date,
                    duration_minutes,
                    location,
                    attendees,
                    notes,
                    photos,
                    created_by,
                    created_at,
                    updated_at
                FROM oversight_actions
                WHERE {where_sql}
                ORDER BY action_date DESC
            """
            
            result = await session.execute(text(query), params)
            
            actions = []
            for row in result:
                actions.append({
                    "id": str(row[0]),
                    "action_id": row[1],
                    "project_id": str(row[2]),
                    "site_visit_id": str(row[3]) if row[3] else None,
                    "licensed_business_id": str(row[4]),
                    "qualifier_id": str(row[5]),
                    "action_type": row[6],
                    "action_date": row[7].isoformat() if row[7] else None,
                    "action_description": row[8],
                    "location": row[9],
                    "duration_hours": row[10],
                    "follow_up_required": row[11],
                    "created_at": row[12].isoformat() if row[12] else None,
                    "updated_at": row[13].isoformat() if row[13] else None
                })
            
            logger.info(f"[OVERSIGHT_ACTIONS] Retrieved {len(actions)} oversight actions")
            return actions
            
    except Exception as e:
        logger.error(f"Failed to get oversight actions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve oversight actions: {str(e)}"
        )


@router.get("/{action_id}")
async def get_oversight_action(action_id: str):
    """
    Get a specific oversight action by ID (UUID or action_id format).
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("""
                SELECT 
                    id,
                    action_id,
                    project_id,
                    site_visit_id,
                    licensed_business_id,
                    qualifier_id,
                    action_type,
                    action_date,
                    action_description,
                    location,
                    duration_hours,
                    attendees,
                    photos,
                    notes,
                    follow_up_required,
                    follow_up_notes,
                    created_at,
                    updated_at
                FROM oversight_actions
                WHERE id::text = :action_id OR action_id = :action_id
            """), {"action_id": action_id})
            
            row = result.fetchone()
            
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Oversight action {action_id} not found"
                )
            
            action = {
                "id": str(row[0]),
                "action_id": row[1],
                "project_id": str(row[2]),
                "site_visit_id": str(row[3]) if row[3] else None,
                "licensed_business_id": str(row[4]),
                "qualifier_id": str(row[5]),
                "action_type": row[6],
                "action_date": row[7].isoformat() if row[7] else None,
                "action_description": row[8],
                "location": row[9],
                "duration_hours": row[10],
                "attendees": row[11],  # JSONB
                "photos": row[12],  # JSONB
                "notes": row[13],
                "follow_up_required": row[14],
                "follow_up_notes": row[15],
                "created_at": row[16].isoformat() if row[16] else None,
                "updated_at": row[17].isoformat() if row[17] else None
            }
            
            return action
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get oversight action {action_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve oversight action: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_oversight_action(
    action_data: OversightActionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new oversight action.
    Protected endpoint - requires authentication.
    Database trigger enforces cutoff_date validation.
    """
    try:
        action_dict = action_data.model_dump()
        
        # Create via db_service
        created_action = await db_service.create_oversight_action(action_dict)
        
        logger.info(f"[OVERSIGHT_ACTIONS] Created action {created_action.get('action_id')} by user {current_user.email}")
        return created_action
        
    except Exception as e:
        logger.error(f"Failed to create oversight action: {e}", exc_info=True)
        
        # Check if trigger blocked due to cutoff_date
        if "cutoff" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Oversight action blocked: {str(e)}"
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create oversight action: {str(e)}"
        )


@router.put("/{action_id}")
async def update_oversight_action(
    action_id: str,
    action_data: OversightActionUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing oversight action.
    Protected endpoint - requires authentication.
    action_id can be UUID or action_id format (OA-00001).
    """
    try:
        update_dict = action_data.model_dump(exclude_unset=True)
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Find and update action
        async with AsyncSessionLocal() as session:
            stmt = select(OversightAction).where(
                (OversightAction.id == action_id) | (OversightAction.action_id == action_id)
            )
            result = await session.execute(stmt)
            action = result.scalar_one_or_none()
            
            if not action:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Oversight action {action_id} not found"
                )
            
            # Update fields
            for key, value in update_dict.items():
                if hasattr(action, key):
                    setattr(action, key, value)
            
            await session.commit()
            await session.refresh(action)
            
            logger.info(f"[OVERSIGHT_ACTIONS] Updated action {action_id} by user {current_user.email}")
            
            return {
                "id": str(action.id),
                "action_id": action.action_id,
                "project_id": str(action.project_id),
                "action_type": action.action_type,
                "action_date": action.action_date.isoformat() if action.action_date else None,
                "action_description": action.action_description,
                "updated_at": action.updated_at.isoformat() if action.updated_at else None
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update oversight action {action_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update oversight action: {str(e)}"
        )


@router.delete("/{action_id}")
async def delete_oversight_action(
    action_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an oversight action (hard delete).
    Protected endpoint - requires authentication.
    action_id can be UUID or action_id format (OA-00001).
    """
    try:
        async with AsyncSessionLocal() as session:
            stmt = select(OversightAction).where(
                (OversightAction.id == action_id) | (OversightAction.action_id == action_id)
            )
            result = await session.execute(stmt)
            action = result.scalar_one_or_none()
            
            if not action:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Oversight action {action_id} not found"
                )
            
            await session.delete(action)
            await session.commit()
            
            logger.info(f"[OVERSIGHT_ACTIONS] Deleted action {action_id} by user {current_user.email}")
            return {"message": f"Oversight action {action_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete oversight action {action_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete oversight action: {str(e)}"
        )
