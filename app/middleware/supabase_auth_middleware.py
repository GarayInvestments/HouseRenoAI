"""
JWT Authentication Middleware for Supabase Auth

Protects routes by verifying Supabase JWT tokens in Authorization header.
Maps Supabase auth users to app users automatically.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.supabase_auth_service import supabase_auth_service
from app.db.session import AsyncSessionLocal
import logging

logger = logging.getLogger(__name__)


class SupabaseJWTMiddleware(BaseHTTPMiddleware):
    """Middleware to verify Supabase JWT tokens on protected routes"""
    
    # Routes that don't require authentication
    PUBLIC_ROUTES = [
        "/",
        "/health",
        "/debug",
        "/version",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/v1/auth/health",
        "/privacy",
        "/terms",
    ]
    
    async def dispatch(self, request: Request, call_next):
        """Check JWT token for protected routes"""
        
        # Check if route is public
        path = request.url.path
        
        # Allow public routes
        if any(path.startswith(route) for route in self.PUBLIC_ROUTES):
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header missing"}
            )
        
        # Check Bearer token format
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header format. Use: Bearer <token>"}
            )
        
        token = parts[1]
        
        # Verify JWT using Supabase
        payload = supabase_auth_service.verify_jwt(token)
        if not payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"}
            )
        
        # Extract user info from JWT
        supabase_user_id = payload.get("sub")
        email = payload.get("email")
        user_metadata = payload.get("user_metadata", {})
        
        if not supabase_user_id or not email:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token payload"}
            )
        
        # Get or create user in app database
        async with AsyncSessionLocal() as db:
            try:
                user = await supabase_auth_service.get_or_create_user(
                    db=db,
                    supabase_user_id=supabase_user_id,
                    email=email,
                    user_metadata=user_metadata
                )
                
                if not user or not user.is_active:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "User account is deactivated"}
                    )
                
                # Add user info to request state
                request.state.user_id = user.id
                request.state.user_email = user.email
                request.state.user_role = user.role
                request.state.supabase_user_id = supabase_user_id
                
            except Exception as e:
                logger.error(f"Error getting/creating user in middleware: {e}", exc_info=True)
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Internal server error during authentication"}
                )
        
        # Continue to route handler
        response = await call_next(request)
        return response
