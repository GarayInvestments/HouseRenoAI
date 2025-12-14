from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
import logging
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.services.db_service import db_service
from app.routes.auth_supabase import get_current_user
from app.db.models import User
from app.routes.licensed_businesses_pydantic import (
    LicensedBusinessCreate,
    LicensedBusinessUpdate
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_licensed_businesses():
    """
    Get all licensed businesses for dropdown selection
    Returns: List of {id, business_id, business_name, license_number, license_status}
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("""
                SELECT 
                    id,
                    business_id,
                    business_name,
                    license_number,
                    license_status,
                    active
                FROM licensed_businesses
                WHERE active = true
                ORDER BY business_name
            """))
            
            businesses = []
            for row in result:
                businesses.append({
                    "id": str(row[0]),
                    "business_id": row[1],
                    "business_name": row[2],
                    "license_number": row[3],
                    "license_status": row[4],
                    "active": row[5]
                })
            
            logger.info(f"Retrieved {len(businesses)} licensed businesses")
            return businesses
            
    except Exception as e:
        logger.error(f"Failed to get licensed businesses: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve licensed businesses: {str(e)}")


@router.get("/{business_id}")
async def get_licensed_business(business_id: str):
    """
    Get a specific licensed business by ID (UUID or business_id format)
    """
    try:
        async with AsyncSessionLocal() as session:
            # Try both UUID and business_id format
            result = await session.execute(text("""
                SELECT 
                    id,
                    business_id,
                    business_name,
                    legal_name,
                    license_number,
                    license_type,
                    license_status,
                    license_issue_date,
                    license_expiration_date,
                    active,
                    address,
                    phone,
                    email,
                    notes,
                    created_at,
                    updated_at
                FROM licensed_businesses
                WHERE id::text = :business_id OR business_id = :business_id
            """), {"business_id": business_id})
            
            row = result.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Licensed business {business_id} not found")
            
            business = {
                "id": str(row[0]),
                "business_id": row[1],
                "business_name": row[2],
                "legal_name": row[3],
                "license_number": row[4],
                "license_type": row[5],
                "license_status": row[6],
                "license_issue_date": row[7].isoformat() if row[7] else None,
                "license_expiration_date": row[8].isoformat() if row[8] else None,
                "active": row[9],
                "address": row[10],
                "phone": row[11],
                "email": row[12],
                "notes": row[13],
                "created_at": row[14].isoformat() if row[14] else None,
                "updated_at": row[15].isoformat() if row[15] else None
            }
            
            return business
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get licensed business {business_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve licensed business: {str(e)}")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_licensed_business(
    business_data: LicensedBusinessCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new licensed business.
    Protected endpoint - requires authentication.
    """
    try:
        business_dict = business_data.model_dump()
        
        # Create via db_service
        created_business = await db_service.create_licensed_business(business_dict)
        
        logger.info(f"[LICENSED_BUSINESSES] Created business {created_business.get('business_id')} by user {current_user.email}")
        return created_business
        
    except Exception as e:
        logger.error(f"Failed to create licensed business: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create licensed business: {str(e)}"
        )


@router.put("/{business_id}")
async def update_licensed_business(
    business_id: str,
    business_data: LicensedBusinessUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing licensed business.
    Protected endpoint - requires authentication.
    business_id can be UUID or business_id format (LB-00001).
    """
    try:
        # Convert to dict, exclude unset fields
        update_dict = business_data.model_dump(exclude_unset=True)
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update via db_service
        updated_business = await db_service.update_licensed_business(business_id, update_dict)
        
        if not updated_business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Licensed business {business_id} not found"
            )
        
        logger.info(f"[LICENSED_BUSINESSES] Updated business {business_id} by user {current_user.email}")
        return updated_business
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update licensed business {business_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update licensed business: {str(e)}"
        )


@router.delete("/{business_id}")
async def delete_licensed_business(
    business_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete (soft delete) a licensed business by setting active=False.
    Protected endpoint - requires authentication.
    business_id can be UUID or business_id format (LB-00001).
    """
    try:
        # Soft delete by updating active flag
        updated_business = await db_service.update_licensed_business(
            business_id,
            {"is_active": False}
        )
        
        if not updated_business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Licensed business {business_id} not found"
            )
        
        logger.info(f"[LICENSED_BUSINESSES] Deleted (soft) business {business_id} by user {current_user.email}")
        return {"message": f"Licensed business {business_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete licensed business {business_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete licensed business: {str(e)}"
        )
