"""
API routes for user management (admin only).
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from pydantic import BaseModel, EmailStr
import logging

from app.services.db_service import db_service

logger = logging.getLogger(__name__)
router = APIRouter()


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: str = "client"  # admin, pm, inspector, client, finance


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/")
async def get_all_users():
    """Get all users (admin only)"""
    try:
        users = await db_service.get_users_data()
        return users
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
async def get_user(user_id: str):
    """Get a specific user"""
    try:
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Create a new user (admin only)"""
    try:
        user_dict = user_data.model_dump(exclude_none=True)
        new_user = await db_service.create_user(user_dict)
        return new_user
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}")
async def update_user(user_id: str, user_data: UserUpdate):
    """Update a user (admin only)"""
    try:
        update_dict = user_data.model_dump(exclude_none=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        updated_user = await db_service.update_user(user_id, update_dict)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    """Delete a user (admin only)"""
    try:
        deleted = await db_service.delete_user(user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/role")
async def update_user_role(user_id: str, role: str):
    """Update user role (admin only)"""
    try:
        updated_user = await db_service.update_user(user_id, {"role": role})
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/activate")
async def activate_user(user_id: str):
    """Activate a user (admin only)"""
    try:
        updated_user = await db_service.update_user(user_id, {"is_active": True})
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/deactivate")
async def deactivate_user(user_id: str):
    """Deactivate a user (admin only)"""
    try:
        updated_user = await db_service.update_user(user_id, {"is_active": False})
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
