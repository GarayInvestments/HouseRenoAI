"""
API routes for jurisdiction management.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional, Dict, Any
from pydantic import BaseModel
import logging

from app.services.db_service import db_service

logger = logging.getLogger(__name__)
router = APIRouter()


class JurisdictionCreate(BaseModel):
    name: str
    state: str
    requirements: Optional[Dict[str, Any]] = {}


class JurisdictionUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None


@router.get("/")
async def get_all_jurisdictions():
    """Get all jurisdictions"""
    try:
        jurisdictions = await db_service.get_jurisdictions_data()
        return jurisdictions
    except Exception as e:
        logger.error(f"Failed to get jurisdictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{jurisdiction_id}")
async def get_jurisdiction(jurisdiction_id: str):
    """Get a specific jurisdiction"""
    try:
        jurisdiction = await db_service.get_jurisdiction_by_id(jurisdiction_id)
        if not jurisdiction:
            raise HTTPException(status_code=404, detail=f"Jurisdiction {jurisdiction_id} not found")
        return jurisdiction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_jurisdiction(jurisdiction_data: JurisdictionCreate):
    """Create a new jurisdiction"""
    try:
        jurisdiction_dict = jurisdiction_data.model_dump(exclude_none=True)
        new_jurisdiction = await db_service.create_jurisdiction(jurisdiction_dict)
        return new_jurisdiction
    except Exception as e:
        logger.error(f"Failed to create jurisdiction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{jurisdiction_id}")
async def update_jurisdiction(jurisdiction_id: str, jurisdiction_data: JurisdictionUpdate):
    """Update a jurisdiction"""
    try:
        update_dict = jurisdiction_data.model_dump(exclude_none=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        updated_jurisdiction = await db_service.update_jurisdiction(jurisdiction_id, update_dict)
        return updated_jurisdiction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{jurisdiction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_jurisdiction(jurisdiction_id: str):
    """Delete a jurisdiction"""
    try:
        deleted = await db_service.delete_jurisdiction(jurisdiction_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Jurisdiction {jurisdiction_id} not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
