from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
import logging
from sqlalchemy import text

from app.db.session import AsyncSessionLocal
from app.services.db_service import db_service
from app.routes.auth_supabase import get_current_user
from app.db.models import User
from app.routes.qualifiers_pydantic import (
    QualifierCreate,
    QualifierUpdate,
    QualifierAssignmentCreate,
    QualifierAssignmentUpdate
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_qualifiers():
    """
    Get all qualifiers for dropdown selection
    Returns: List of {id, qualifier_id, full_name, qualifier_id_number, license_status}
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("""
                SELECT 
                    id,
                    qualifier_id,
                    full_name,
                    qualifier_id_number,
                    license_type,
                    license_status,
                    max_licenses_allowed
                FROM qualifiers
                WHERE license_status = 'active'
                ORDER BY full_name
            """))
            
            qualifiers = []
            for row in result:
                qualifiers.append({
                    "id": str(row[0]),
                    "qualifier_id": row[1],
                    "full_name": row[2],
                    "qualifier_id_number": row[3],
                    "license_type": row[4],
                    "license_status": row[5],
                    "max_licenses_allowed": row[6]
                })
            
            logger.info(f"Retrieved {len(qualifiers)} qualifiers")
            return qualifiers
            
    except Exception as e:
        logger.error(f"Failed to get qualifiers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve qualifiers: {str(e)}")


@router.get("/{qualifier_id}")
async def get_qualifier(qualifier_id: str):
    """
    Get a specific qualifier by ID (UUID or qualifier_id format)
    """
    try:
        async with AsyncSessionLocal() as session:
            # Try both UUID and qualifier_id format
            result = await session.execute(text("""
                SELECT 
                    id,
                    qualifier_id,
                    user_id,
                    full_name,
                    qualifier_id_number,
                    license_type,
                    license_status,
                    license_issue_date,
                    license_expiration_date,
                    max_licenses_allowed,
                    email,
                    phone,
                    notes,
                    created_at,
                    updated_at
                FROM qualifiers
                WHERE id::text = :qualifier_id OR qualifier_id = :qualifier_id
            """), {"qualifier_id": qualifier_id})
            
            row = result.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Qualifier {qualifier_id} not found")
            
            qualifier = {
                "id": str(row[0]),
                "qualifier_id": row[1],
                "user_id": str(row[2]),
                "full_name": row[3],
                "qualifier_id_number": row[4],
                "license_type": row[5],
                "license_status": row[6],
                "license_issue_date": row[7].isoformat() if row[7] else None,
                "license_expiration_date": row[8].isoformat() if row[8] else None,
                "max_licenses_allowed": row[9],
                "email": row[10],
                "phone": row[11],
                "notes": row[12],
                "created_at": row[13].isoformat() if row[13] else None,
                "updated_at": row[14].isoformat() if row[14] else None
            }
            
            return qualifier
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get qualifier {qualifier_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve qualifier: {str(e)}")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_qualifier(
    qualifier_data: QualifierCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new qualifier (must link to existing user).
    Protected endpoint - requires authentication.
    """
    try:
        qualifier_dict = qualifier_data.model_dump()
        
        # Create via db_service
        created_qualifier = await db_service.create_qualifier(qualifier_dict)
        
        logger.info(f"[QUALIFIERS] Created qualifier {created_qualifier.get('qualifier_id')} by user {current_user.email}")
        return created_qualifier
        
    except Exception as e:
        logger.error(f"Failed to create qualifier: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create qualifier: {str(e)}"
        )


@router.put("/{qualifier_id}")
async def update_qualifier(
    qualifier_id: str,
    qualifier_data: QualifierUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing qualifier.
    Protected endpoint - requires authentication.
    qualifier_id can be UUID or qualifier_id format (QF-00001).
    """
    try:
        update_dict = qualifier_data.model_dump(exclude_unset=True)
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update via db_service
        updated_qualifier = await db_service.update_qualifier(qualifier_id, update_dict)
        
        if not updated_qualifier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Qualifier {qualifier_id} not found"
            )
        
        logger.info(f"[QUALIFIERS] Updated qualifier {qualifier_id} by user {current_user.email}")
        return updated_qualifier
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update qualifier {qualifier_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update qualifier: {str(e)}"
        )


@router.delete("/{qualifier_id}")
async def delete_qualifier(
    qualifier_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete (soft delete) a qualifier by setting is_active=False.
    Protected endpoint - requires authentication.
    qualifier_id can be UUID or qualifier_id format (QF-00001).
    """
    try:
        # Soft delete by updating is_active flag
        updated_qualifier = await db_service.update_qualifier(
            qualifier_id,
            {"is_active": False}
        )
        
        if not updated_qualifier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Qualifier {qualifier_id} not found"
            )
        
        logger.info(f"[QUALIFIERS] Deleted (soft) qualifier {qualifier_id} by user {current_user.email}")
        return {"message": f"Qualifier {qualifier_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete qualifier {qualifier_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete qualifier: {str(e)}"
        )


@router.post("/{qualifier_id}/assign", status_code=status.HTTP_201_CREATED)
async def assign_qualifier_to_business(
    qualifier_id: str,
    assignment_data: QualifierAssignmentCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Assign a qualifier to a licensed business.
    Validates capacity (max 2 licenses per NC law).
    Protected endpoint - requires authentication.
    """
    try:
        # Check capacity before assigning
        capacity_check = await db_service.check_qualifier_capacity(qualifier_id)
        
        if not capacity_check["can_assign"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Qualifier at capacity: {capacity_check['current_count']}/{capacity_check['max_allowed']} licenses"
            )
        
        # Create assignment
        assignment_dict = {
            "licensed_business_id": assignment_data.licensed_business_id,
            "qualifier_id": qualifier_id,
            "start_date": assignment_data.start_date,
            "end_date": assignment_data.end_date,
            "cutoff_date": assignment_data.cutoff_date,
            "is_primary": assignment_data.is_primary,
            "assignment_notes": assignment_data.assignment_notes
        }
        
        created_assignment = await db_service.assign_qualifier_to_business(
            assignment_dict["licensed_business_id"],
            qualifier_id,
            assignment_dict["start_date"],
            assignment_dict.get("end_date"),
            assignment_dict.get("cutoff_date"),
            assignment_dict.get("is_primary", True),
            assignment_dict.get("assignment_notes")
        )
        
        logger.info(f"[QUALIFIERS] Assigned qualifier {qualifier_id} to business {assignment_data.licensed_business_id} by user {current_user.email}")
        return created_assignment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assign qualifier {qualifier_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign qualifier: {str(e)}"
        )


@router.get("/{qualifier_id}/capacity")
async def check_qualifier_capacity(qualifier_id: str):
    """
    Check if qualifier has capacity to take on additional licenses.
    Returns current_count, max_allowed, remaining, can_assign.
    """
    try:
        capacity = await db_service.check_qualifier_capacity(qualifier_id)
        return capacity
        
    except Exception as e:
        logger.error(f"Failed to check qualifier capacity {qualifier_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check capacity: {str(e)}"
        )
