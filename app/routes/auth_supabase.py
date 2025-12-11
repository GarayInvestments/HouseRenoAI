"""
Authentication routes for Supabase Auth integration.

Frontend flow:
1. User signs up/logs in via Supabase client SDK (@supabase/supabase-js)
2. Supabase returns JWT access token
3. Frontend sends token in Authorization: Bearer <token>
4. Backend verifies token and maps to app user

Backend provides:
- /me endpoint to get current user info
- /admin endpoints for user management (role updates)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.supabase_auth_service import supabase_auth_service
from app.db.models import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


# Response models
class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: str
    is_active: bool
    is_email_verified: bool
    last_login_at: Optional[str] = None
    app_metadata: Optional[Dict[str, Any]] = None
    created_at: str
    
    class Config:
        from_attributes = True


class UpdateRoleRequest(BaseModel):
    user_id: str
    role: str  # admin, pm, inspector, client, finance


class UpdateMetadataRequest(BaseModel):
    metadata: Dict[str, Any]


# Dependency to get current user from Supabase JWT
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Verify Supabase JWT token and return current user.
    
    Flow:
    1. Extract JWT from Authorization header
    2. Verify JWT using Supabase JWT secret or JWKS
    3. Get or create user in app database
    4. Return User model
    """
    token = credentials.credentials
    
    # Verify JWT
    payload = supabase_auth_service.verify_jwt(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user info from JWT
    supabase_user_id = payload.get("sub")
    email = payload.get("email")
    user_metadata = payload.get("user_metadata", {})
    
    if not supabase_user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get or create app user
    user = await supabase_auth_service.get_or_create_user(
        db=db,
        supabase_user_id=supabase_user_id,
        email=email,
        user_metadata=user_metadata
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get or create user"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user


# Dependency for admin-only routes
async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify current user has admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user info.
    
    Frontend should call this after login to get app-specific user data (role, permissions).
    """
    return current_user


@router.put("/me/metadata", response_model=UserResponse)
async def update_my_metadata(
    request: UpdateMetadataRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's app metadata (preferences, settings).
    
    Example metadata:
    {
        "preferences": {"theme": "dark", "notifications": true},
        "settings": {"email_updates": false}
    }
    """
    success = await supabase_auth_service.update_user_metadata(
        db=db,
        user_id=current_user.id,
        metadata=request.metadata
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update metadata"
        )
    
    # Refresh user
    await db.refresh(current_user)
    return current_user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    _: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID (admin only)"""
    user = await supabase_auth_service.get_user_by_id(db=db, user_id=user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    request: UpdateRoleRequest,
    _: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user role (admin only).
    
    Valid roles: admin, pm, inspector, client, finance
    """
    success = await supabase_auth_service.update_user_role(
        db=db,
        user_id=user_id,
        role=request.role
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update role (invalid role or user not found)"
        )
    
    # Get updated user
    user = await supabase_auth_service.get_user_by_id(db=db, user_id=user_id)
    return user


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    _: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate user (soft delete, admin only)"""
    success = await supabase_auth_service.deactivate_user(db=db, user_id=user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deactivated successfully"}


@router.get("/health")
async def auth_health():
    """Check auth service health"""
    return {
        "status": "healthy",
        "supabase_url": supabase_auth_service.supabase_url,
        "jwt_verification": "jwt_secret" if supabase_auth_service.jwt_secret else "jwks"
    }
