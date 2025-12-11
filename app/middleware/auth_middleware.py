"""
JWT Authentication Middleware for House Renovators AI Portal
Protects routes by verifying JWT tokens in Authorization header
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)

class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to verify JWT tokens on protected routes"""
    
    # Routes that don't require authentication
    PUBLIC_ROUTES = [
        "/",
        "/health",
        "/debug",
        "/version",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/v1/auth/login",
        "/v1/auth/register",
        "/v1/auth/supabase",  # All Supabase auth routes are public (they handle their own auth)
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
        
        # Verify token
        payload = auth_service.verify_token(token)
        if not payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"}
            )
        
        # Add user info to request state
        request.state.user_email = payload.get("sub")
        request.state.user_role = payload.get("role", "user")
        
        # Continue to route handler
        response = await call_next(request)
        return response
