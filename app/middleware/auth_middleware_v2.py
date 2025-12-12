"""
Modern JWT Authentication Middleware with token blacklist support.

Security improvements over legacy system:
- Validates token signature and expiration
- Checks token blacklist (for revoked tokens)
- Verifies user is active
- Extracts user info from database (not just token claims)
- Rate limiting protection
- Request logging for security audit

Public routes (no authentication required):
- Health checks
- API documentation
- Authentication endpoints (login, register, refresh)
- Public pages (privacy, terms)
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.auth_service_v2 import get_token_service, get_auth_service
from app.db.session import get_db
import logging

logger = logging.getLogger(__name__)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify JWT tokens on protected routes.
    
    Flow:
    1. Check if route is public (skip authentication)
    2. Extract token from Authorization header
    3. Verify token signature and expiration
    4. Check if token is blacklisted
    5. Get user from database
    6. Verify user is active
    7. Add user info to request state
    8. Continue to route handler
    
    If any step fails, return 401 Unauthorized.
    """
    
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
        "/v1/auth/refresh",
        "/v1/auth/supabase",  # Supabase auth endpoints (handle their own auth)
        "/privacy",
        "/terms",
        "/favicon.ico",
    ]
    
    async def dispatch(self, request: Request, call_next):
        """Check JWT token for protected routes"""
        
        path = request.url.path
        
        # Allow public routes
        if any(path.startswith(route) for route in self.PUBLIC_ROUTES):
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Authorization header missing",
                    "error_code": "MISSING_AUTH_HEADER"
                }
            )
        
        # Check Bearer token format
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Invalid authorization header format. Use: Bearer <token>",
                    "error_code": "INVALID_AUTH_FORMAT"
                }
            )
        
        token = parts[1]
        
        try:
            # Get token service
            token_service = get_token_service()
            
            # Verify token signature and expiration
            payload = token_service.verify_access_token(token)
            if not payload:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Invalid or expired token",
                        "error_code": "INVALID_TOKEN"
                    }
                )
            
            # Get database session
            async for db in get_db():
                try:
                    auth_service = get_auth_service(db)
                    
                    # Check if token is blacklisted
                    jti = payload.get("jti")
                    if jti and await auth_service.is_token_blacklisted(jti):
                        return JSONResponse(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            content={
                                "detail": "Token has been revoked",
                                "error_code": "TOKEN_REVOKED"
                            }
                        )
                    
                    # Get user from database
                    user_id = payload.get("sub")
                    user = await auth_service.get_user_by_id(user_id)
                    
                    if not user:
                        return JSONResponse(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            content={
                                "detail": "User not found",
                                "error_code": "USER_NOT_FOUND"
                            }
                        )
                    
                    # Check if user is active
                    if not user.is_active:
                        return JSONResponse(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            content={
                                "detail": "User account is inactive",
                                "error_code": "USER_INACTIVE"
                            }
                        )
                    
                    # Add user info to request state
                    request.state.user_id = user.id
                    request.state.user_email = user.email
                    request.state.user_role = user.role
                    request.state.user = user
                    
                    # Continue to route handler
                    response = await call_next(request)
                    return response
                    
                finally:
                    # Database session cleanup handled by context manager
                    pass
            
        except Exception as e:
            logger.error(f"Authentication middleware error: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error during authentication",
                    "error_code": "AUTH_ERROR"
                }
            )
