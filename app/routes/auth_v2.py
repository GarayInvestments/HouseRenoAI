"""
Modern authentication routes with refresh token rotation.

Endpoints:
- POST /v1/auth/login - Login with email/password
- POST /v1/auth/register - Register new user
- POST /v1/auth/refresh - Refresh access token
- POST /v1/auth/logout - Logout (revoke tokens)
- POST /v1/auth/logout-all - Logout from all devices
- GET /v1/auth/me - Get current user info
- GET /v1/auth/sessions - Get active sessions
- DELETE /v1/auth/sessions/{session_id} - Revoke specific session

Security features:
- Rate limiting on login
- Token blacklist for immediate revocation
- Refresh token rotation (prevents replay attacks)
- Session management
- Device tracking
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service_v2 import get_auth_service, get_token_service, AuthService, TokenService
from app.db.session import get_db
from app.db.models import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


# ==================== Request/Response Models ====================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_name: Optional[str] = None  # e.g., "Chrome on Windows", "iOS App"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes in seconds
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_email_verified: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime


class SessionResponse(BaseModel):
    id: str
    device_name: Optional[str]
    device_type: Optional[str]
    browser: Optional[str]
    os: Optional[str]
    ip_address: Optional[str]
    location: Optional[str]
    last_activity_at: datetime
    created_at: datetime
    is_current: bool = False


class MessageResponse(BaseModel):
    message: str


# ==================== Dependencies ====================

def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP address from request"""
    # Check X-Forwarded-For header (behind proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection IP
    if request.client:
        return request.client.host
    
    return None


def get_user_agent(request: Request) -> Optional[str]:
    """Extract user agent from request"""
    return request.headers.get("User-Agent")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user.
    
    Verifies:
    1. Token is valid (not expired, proper signature)
    2. Token is not blacklisted
    3. User exists and is active
    
    Raises HTTP 401 if any check fails.
    """
    token = credentials.credentials
    token_service = get_token_service()
    auth_service = get_auth_service(db)
    
    # Verify token
    payload = token_service.verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if token is blacklisted
    jti = payload.get("jti")
    if jti and await auth_service.is_token_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user_id = payload.get("sub")
    user = await auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    return user


# ==================== Authentication Endpoints ====================

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email/password.
    
    Returns access token (15 min) and refresh token (30 days).
    Access token is used for API requests.
    Refresh token is used to get new access tokens when they expire.
    
    Security:
    - Rate limited (5 attempts per 15 minutes per email)
    - Login attempts logged for security monitoring
    - Session created for device tracking
    """
    try:
        ip_address = get_client_ip(http_request)
        user_agent = get_user_agent(http_request)
        auth_service = get_auth_service(db)
        
        # Check rate limit
        is_allowed, attempts_remaining = await auth_service.check_rate_limit(
            request.email, 
            ip_address
        )
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again in 15 minutes."
            )
        
        # Authenticate user
        user = await auth_service.authenticate_user(
            email=request.email,
            password=request.password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid email or password. {attempts_remaining - 1} attempts remaining."
            )
        
        # Create session with tokens
        access_token, refresh_token, session = await auth_service.create_session(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            device_name=request.device_name
        )
        
        logger.info(f"User {user.email} logged in from {ip_address}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900,  # 15 minutes
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new user account.
    
    Creates user in local database and links to Supabase Auth.
    Returns access token and refresh token for immediate login.
    
    TODO: Integrate with Supabase Auth API for user creation.
    """
    try:
        ip_address = get_client_ip(http_request)
        user_agent = get_user_agent(http_request)
        auth_service = get_auth_service(db)
        
        # Check if user already exists
        existing_user = await auth_service.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user in database
        # TODO: Create user in Supabase Auth first, then link here
        hashed_password = auth_service.hash_password(request.password)
        
        user = User(
            email=request.email,
            full_name=request.full_name,
            phone=request.phone,
            password_hash=hashed_password,
            supabase_user_id=None,  # Local user, no Supabase Auth integration yet
            role="client",  # Default role
            is_active=True,
            is_email_verified=False  # TODO: Send verification email
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Create session with tokens
        access_token, refresh_token, session = await auth_service.create_session(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            device_name="Registration"
        )
        
        logger.info(f"User {user.email} registered from {ip_address}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Security: Implements token rotation - old refresh token is invalidated
    and a new one is issued. If an old token is reused, the entire token
    family is revoked (indicates token theft).
    
    Returns new access token and new refresh token.
    """
    try:
        ip_address = get_client_ip(http_request)
        user_agent = get_user_agent(http_request)
        auth_service = get_auth_service(db)
        
        # Refresh tokens (with rotation)
        result = await auth_service.refresh_tokens(
            refresh_token_raw=request.refresh_token,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        new_access_token, new_refresh_token = result
        
        # Decode access token to get user info (for response)
        token_service = get_token_service()
        payload = token_service.verify_access_token(new_access_token)
        
        user = await auth_service.get_user_by_id(payload["sub"])
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 900,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout from current session.
    
    Actions:
    - Blacklist current access token
    - Revoke all refresh tokens for user
    - End all active sessions
    
    User will need to login again on all devices.
    """
    try:
        token = credentials.credentials
        auth_service = get_auth_service(db)
        
        await auth_service.logout(token, current_user.id)
        
        logger.info(f"User {current_user.email} logged out")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout from all devices (security measure).
    
    Use cases:
    - Password reset
    - Security breach
    - Lost device
    
    Revokes ALL tokens and sessions for the user.
    """
    try:
        auth_service = get_auth_service(db)
        
        await auth_service.revoke_all_user_tokens(
            user_id=current_user.id,
            reason="logout_all_requested"
        )
        
        logger.warning(f"User {current_user.email} logged out from all devices")
        
        return {"message": "Successfully logged out from all devices"}
        
    except Exception as e:
        logger.error(f"Logout all error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Requires valid access token in Authorization header.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_email_verified": current_user.is_email_verified,
        "last_login_at": current_user.last_login_at,
        "created_at": current_user.created_at
    }


@router.get("/sessions", response_model=List[SessionResponse])
async def get_active_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all active sessions for current user.
    
    Shows all devices/locations where user is logged in.
    Useful for security monitoring and session management.
    """
    try:
        auth_service = get_auth_service(db)
        sessions = await auth_service.get_active_sessions(current_user.id)
        
        return [
            {
                "id": session.id,
                "device_name": session.device_name,
                "device_type": session.device_type,
                "browser": session.browser,
                "os": session.os,
                "ip_address": str(session.ip_address) if session.ip_address else None,
                "location": session.location,
                "last_activity_at": session.last_activity_at,
                "created_at": session.created_at,
                "is_current": False  # TODO: Detect current session
            }
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Get sessions error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke a specific session (logout from specific device).
    
    Use case: "Sign out from other devices" feature.
    User can see all active sessions and revoke specific ones.
    """
    try:
        auth_service = get_auth_service(db)
        
        success = await auth_service.revoke_session(session_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        logger.info(f"User {current_user.email} revoked session {session_id}")
        
        return {"message": "Session revoked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Revoke session error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
