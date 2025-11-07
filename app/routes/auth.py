"""
Authentication routes for House Renovators AI Portal
Handles login, register, token refresh, and current user info
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.services.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Request/Response models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    email: str
    name: str
    role: str

# Dependency to get current user from token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify token and return current user"""
    token = credentials.credentials
    
    payload = auth_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = await auth_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login endpoint - authenticate user and return JWT token
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT token valid for 7 days
    """
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(request.email, request.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(
            email=user["email"],
            role=user["role"]
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """
    Register endpoint - create new user account
    
    - **email**: User's email address
    - **password**: User's password (will be hashed)
    - **name**: User's full name
    
    Creates user with 'user' role by default
    """
    try:
        # Create user
        success = await auth_service.create_user(
            email=request.email,
            password=request.password,
            name=request.name,
            role="user"
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists or could not be created"
            )
        
        # Get created user
        user = await auth_service.get_user_by_email(request.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User created but could not be retrieved"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(
            email=user["email"],
            role=user["role"]
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user info endpoint
    
    Requires valid JWT token in Authorization header
    Returns current user information
    """
    return {
        "email": current_user["email"],
        "name": current_user["name"],
        "role": current_user["role"]
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Refresh token endpoint
    
    Requires valid JWT token in Authorization header
    Returns new token with extended expiration
    """
    try:
        # Create new access token
        access_token = auth_service.create_access_token(
            email=current_user["email"],
            role=current_user["role"]
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "email": current_user["email"],
                "name": current_user["name"],
                "role": current_user["role"]
            }
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )
