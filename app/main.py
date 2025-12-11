from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import os
import json

from app.config import settings
from app.routes.chat import router as chat_router
from app.routes.permits import router as permits_router
from app.routes.inspections import router as inspections_router
from app.routes.projects import router as projects_router
from app.routes.clients import router as clients_router
from app.routes.documents import router as documents_router
from app.routes.quickbooks import router as quickbooks_router
from app.routes.payments import router as payments_router
from app.routes.auth import router as auth_router
from app.routes.auth_supabase import router as auth_supabase_router
from app.middleware.auth_middleware import JWTAuthMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="House Renovators AI Portal API",
    description="AI-powered backend for House Renovators permit management and chat system",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Git commit for version tracking
GIT_COMMIT = "0e8fc6e"

@app.on_event("startup")
async def startup_event():
    """Create service account file from environment variable on startup"""
    try:
        # Check if we have the JSON credentials as environment variable
        service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        service_account_base64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_BASE64")
        
        logger.info(f"Service account JSON found: {service_account_json is not None}")
        logger.info(f"Service account BASE64 found: {service_account_base64 is not None}")
        
        credentials_data = None
        
        # Try base64 first (preferred method)
        if service_account_base64:
            try:
                import base64
                decoded_json = base64.b64decode(service_account_base64).decode('utf-8')
                credentials_data = json.loads(decoded_json)
                logger.info("Successfully loaded credentials from base64 environment variable")
            except Exception as e:
                logger.error(f"Failed to decode base64 credentials: {e}")
        
        # Fallback to regular JSON
        elif service_account_json:
            try:
                logger.info("Parsing service account JSON...")
                credentials_data = json.loads(service_account_json)
                
                # Fix private key newlines if they are double-escaped
                if 'private_key' in credentials_data and '\\n' in credentials_data['private_key']:
                    credentials_data['private_key'] = credentials_data['private_key'].replace('\\n', '\n')
                    logger.info("Fixed private key newlines")
                    
                logger.info("Successfully loaded credentials from JSON environment variable")
            except Exception as e:
                logger.error(f"Failed to parse JSON credentials: {e}")
        
        # Create the service account file if we have credentials
        if credentials_data and not os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE):
            with open(settings.GOOGLE_SERVICE_ACCOUNT_FILE, 'w') as f:
                json.dump(credentials_data, f, indent=2)
            logger.info(f"Created service account file: {settings.GOOGLE_SERVICE_ACCOUNT_FILE}")
            
            # Verify the file was created and is readable
            if os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE):
                with open(settings.GOOGLE_SERVICE_ACCOUNT_FILE, 'r') as f:
                    test_load = json.load(f)
                logger.info(f"Service account file verified, client_email: {test_load.get('client_email')}")
                logger.info(f"Private key length: {len(test_load.get('private_key', ''))}")
                private_key = test_load.get('private_key', '')
                logger.info(f"Private key starts correctly: {private_key.startswith('-----BEGIN PRIVATE KEY-----')}")
                logger.info(f"Private key ends correctly: {private_key.endswith('-----END PRIVATE KEY-----')}")
            
        elif os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE):
            logger.info(f"Service account file already exists: {settings.GOOGLE_SERVICE_ACCOUNT_FILE}")
        else:
            logger.info("No Google Sheets service account credentials - using database only")
            
        # Initialize Google Sheets service ONLY for QuickBooks token storage
        # TODO: Migrate QB tokens to database and remove this
        if os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE):
            try:
                import app.services.google_service as gs
                logger.info("Initializing Google Sheets (QB tokens only)...")
                gs.google_service = gs.GoogleService()
                gs.google_service.initialize()
                logger.info("Google Sheets initialized for QB token storage")
                
                # Load QuickBooks tokens from Google Sheets
                try:
                    from app.services.quickbooks_service import quickbooks_service
                    logger.info("Loading QuickBooks tokens from Google Sheets...")
                    quickbooks_service._load_tokens_from_sheets()
                    
                    if quickbooks_service.is_authenticated():
                        from datetime import datetime, timedelta
                        # Check if token expires soon (within 10 minutes)
                        if quickbooks_service.token_expires_at and datetime.now() >= quickbooks_service.token_expires_at - timedelta(minutes=10):
                            logger.info("QuickBooks token expiring soon, refreshing on startup...")
                            await quickbooks_service.refresh_access_token()
                            logger.info("QuickBooks token refreshed successfully")
                        else:
                            logger.info(f"QuickBooks token valid until {quickbooks_service.token_expires_at}")
                    else:
                        logger.info("QuickBooks not authenticated, skipping token refresh")
                except Exception as qb_error:
                    logger.warning(f"QuickBooks token refresh on startup failed: {qb_error}")
                    
            except Exception as init_error:
                import traceback
                logger.error(f"Failed to initialize Google services: {init_error}")
                logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            logger.warning("Skipping Google service initialization - no service account file")
            
    except Exception as e:
        logger.error(f"Failed to create service account file: {e}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

# Add CORS middleware with permissive settings for Cloudflare Pages
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.(house-renovators-ai-portal|houserenoai)\.pages\.dev",
    allow_origins=[
        "https://portal.houserenovatorsllc.com",  # Production frontend
        "http://localhost:3000",  # Local dev
        "http://localhost:5173",  # Vite dev server (primary)
        "http://localhost:5174",  # Vite dev server (alternate port)
        "https://house-renovators-pwa.pages.dev",  # Cloudflare preview
        "https://house-renovators-ai-portal.pages.dev",  # Cloudflare Pages domain (old)
        "https://houserenoai.pages.dev",  # Cloudflare Pages domain (current)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add middleware to fix redirect scheme behind proxy
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import URL

class HTTPSRedirectFixMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # If request came via HTTPS proxy (Fly.io), ensure redirects use HTTPS
        if request.headers.get("x-forwarded-proto") == "https":
            request.scope["scheme"] = "https"
        response = await call_next(request)
        return response

app.add_middleware(HTTPSRedirectFixMiddleware)

# Add JWT authentication middleware (protects all routes except public ones)
app.add_middleware(JWTAuthMiddleware)

# Include routers
app.include_router(auth_router, prefix=f"/{settings.API_VERSION}/auth", tags=["auth"])  # Old auth (Google Sheets) - will be phased out
app.include_router(auth_supabase_router, prefix=f"/{settings.API_VERSION}/auth/supabase", tags=["auth-supabase"])  # New Supabase auth
app.include_router(chat_router, prefix=f"/{settings.API_VERSION}/chat", tags=["chat"])
app.include_router(permits_router, prefix=f"/{settings.API_VERSION}/permits", tags=["permits"])
app.include_router(inspections_router, prefix=f"/{settings.API_VERSION}/inspections", tags=["inspections"])
app.include_router(projects_router, prefix=f"/{settings.API_VERSION}/projects", tags=["projects"])
app.include_router(clients_router, prefix=f"/{settings.API_VERSION}/clients", tags=["clients"])
app.include_router(documents_router, prefix=f"/{settings.API_VERSION}/documents", tags=["documents"])
app.include_router(quickbooks_router, prefix=f"/{settings.API_VERSION}/quickbooks", tags=["quickbooks"])
app.include_router(payments_router, prefix=f"/{settings.API_VERSION}/payments", tags=["payments"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "House Renovators AI Portal API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # You can add more health checks here (database, external APIs, etc.)
        return {
            "status": "healthy",
            "api_version": settings.API_VERSION,
            "debug_mode": settings.DEBUG
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check service status"""
    try:
        debug_info = {
            "database_url_configured": bool(settings.DATABASE_URL),
            "supabase_url_configured": bool(settings.SUPABASE_URL),
            "quickbooks_configured": {
                "client_id": bool(settings.QUICKBOOKS_CLIENT_ID),
                "environment": settings.QUICKBOOKS_ENVIRONMENT
            },
            "google_sheets_for_qb_tokens": os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE) if hasattr(settings, 'GOOGLE_SERVICE_ACCOUNT_FILE') else False
        }
        
        return debug_info
        
    except Exception as e:
        logger.error(f"Debug check failed: {e}")
        return {"error": str(e)}

@app.get("/version")
async def get_version():
    """Get deployed version info"""
    return {
        "version": "1.0.0",
        "git_commit": GIT_COMMIT,
        "database": "PostgreSQL (Supabase)"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.DEBUG
    )
