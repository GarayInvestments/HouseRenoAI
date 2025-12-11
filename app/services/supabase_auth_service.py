"""
Supabase Auth Service for House Renovators AI Portal

Handles authentication using Supabase Auth:
- JWT verification using Supabase's JWT secret
- User management (create, get, update)
- Maps Supabase auth.users to app users table
- Role-based access control (RBAC)

Best practices implemented:
- Supabase handles password hashing, email verification, token generation
- App handles role management and app-specific metadata
- JWT verification using Supabase's JWKS endpoint
- Automatic user sync from auth.users to app users table
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import jwt
from jwt import PyJWKClient
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import User
from app.db.session import get_db
import logging

logger = logging.getLogger(__name__)


class SupabaseAuthService:
    """
    Supabase Auth integration service.
    
    Responsibilities:
    - Verify JWTs from Supabase Auth
    - Map Supabase users to app users
    - Manage app-specific user roles and permissions
    """
    
    def __init__(self):
        """Initialize Supabase JWT verification"""
        self.supabase_url = settings.SUPABASE_URL
        self.jwt_secret = settings.SUPABASE_JWT_SECRET
        
        # JWT verification using JWKS (JSON Web Key Set)
        self.jwks_client = None
        if self.supabase_url:
            jwks_url = f"{self.supabase_url}/auth/v1/jwks"
            self.jwks_client = PyJWKClient(jwks_url)
    
    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token from Supabase Auth.
        
        Args:
            token: JWT access token from Supabase
            
        Returns:
            Decoded payload if valid, None if invalid
        """
        try:
            # Method 1: Verify using JWT secret (faster, requires secret)
            if self.jwt_secret:
                payload = jwt.decode(
                    token,
                    self.jwt_secret,
                    algorithms=["HS256"],
                    audience="authenticated",
                    options={"verify_aud": True}
                )
                return payload
            
            # Method 2: Verify using JWKS (no secret needed)
            elif self.jwks_client:
                signing_key = self.jwks_client.get_signing_key_from_jwt(token)
                payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256"],
                    audience="authenticated",
                    options={"verify_aud": True}
                )
                return payload
            
            else:
                logger.error("No JWT verification method available (need SUPABASE_JWT_SECRET or SUPABASE_URL)")
                return None
                
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"JWT verification error: {e}", exc_info=True)
            return None
    
    async def get_or_create_user(self, db: AsyncSession, supabase_user_id: str, email: str, user_metadata: Dict = None) -> Optional[User]:
        """
        Get or create app user from Supabase auth user.
        
        Args:
            db: Database session
            supabase_user_id: Supabase auth.users.id
            email: User email
            user_metadata: Optional metadata from Supabase (full_name, etc.)
            
        Returns:
            User model instance
        """
        try:
            # Check if user exists
            result = await db.execute(
                select(User).where(User.supabase_user_id == supabase_user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                # Update last activity
                user.last_activity_at = datetime.now(timezone.utc)
                await db.commit()
                return user
            
            # Create new user
            full_name = None
            if user_metadata:
                full_name = user_metadata.get('full_name') or user_metadata.get('name')
            
            user = User(
                supabase_user_id=supabase_user_id,
                email=email,
                full_name=full_name,
                role="client",  # Default role
                is_active=True,
                is_email_verified=True,  # Supabase handles verification
                last_activity_at=datetime.now(timezone.utc)
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Created new user: {email} (supabase_id: {supabase_user_id})")
            return user
            
        except Exception as e:
            logger.error(f"Error getting/creating user: {e}", exc_info=True)
            await db.rollback()
            return None
    
    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by internal UUID"""
        try:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            result = await db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    async def update_user_role(self, db: AsyncSession, user_id: str, role: str) -> bool:
        """
        Update user role (admin operation).
        
        Valid roles: admin, pm, inspector, client, finance
        """
        valid_roles = ["admin", "pm", "inspector", "client", "finance"]
        if role not in valid_roles:
            logger.error(f"Invalid role: {role}")
            return False
        
        try:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            user.role = role
            user.updated_at = datetime.now(timezone.utc)
            await db.commit()
            
            logger.info(f"Updated user {user.email} role to {role}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            await db.rollback()
            return False
    
    async def update_user_metadata(self, db: AsyncSession, user_id: str, metadata: Dict[str, Any]) -> bool:
        """Update user app_metadata (permissions, preferences, etc.)"""
        try:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            # Merge metadata (don't overwrite entire object)
            current_metadata = user.app_metadata or {}
            current_metadata.update(metadata)
            user.app_metadata = current_metadata
            user.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating user metadata: {e}")
            await db.rollback()
            return False
    
    async def deactivate_user(self, db: AsyncSession, user_id: str) -> bool:
        """Deactivate user (soft delete)"""
        try:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)
            await db.commit()
            
            logger.info(f"Deactivated user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            await db.rollback()
            return False
    
    async def record_login(self, db: AsyncSession, user_id: str) -> bool:
        """Record user login timestamp"""
        try:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            now = datetime.now(timezone.utc)
            user.last_login_at = now
            user.last_activity_at = now
            await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording login: {e}")
            await db.rollback()
            return False


# Singleton instance
supabase_auth_service = SupabaseAuthService()
