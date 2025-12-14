from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging
from sqlalchemy import text

from app.db.session import AsyncSessionLocal

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
