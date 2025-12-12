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
from app.routes.invoices import router as invoices_router
from app.routes.site_visits import router as site_visits_router
from app.routes.jurisdictions import router as jurisdictions_router
from app.routes.users import router as users_router
from app.routes.auth import router as auth_router
from app.routes.auth_supabase import router as auth_supabase_router
from app.middleware.auth_middleware import JWTAuthMiddleware as LegacyJWTAuthMiddleware

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
    """Initialize services on startup - database-only mode"""
    try:
        logger.info("Application starting up (database-only mode)...")
        
        # Load QuickBooks tokens from database
        try:
            from app.services.quickbooks_service import quickbooks_service
            from app.db.session import get_db
            
            logger.info("Loading QuickBooks tokens from database...")
            
            # Get database session
            db = None
            try:
                db_gen = get_db()
                db = await anext(db_gen)
                quickbooks_service.set_db_session(db)
                
                # Load tokens from database
                await quickbooks_service._load_tokens_from_db()
                
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
                    logger.info("QuickBooks not authenticated - connect at /v1/quickbooks/auth")
            finally:
                if db:
                    await db.close()
                    
        except Exception as qb_error:
            logger.warning(f"QuickBooks token load from database failed: {qb_error}")
            logger.info("QuickBooks will use database storage once OAuth flow is completed")
            
    except Exception as e:
        logger.error(f"Startup error: {e}")
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

# Include routers
app.include_router(auth_supabase_router, prefix=f"/{settings.API_VERSION}/auth/supabase", tags=["auth-supabase"])  # Supabase integration
# app.include_router(auth_router, prefix=f"/{settings.API_VERSION}/auth/legacy", tags=["auth-legacy"])  # Legacy auth (disabled)
app.include_router(chat_router, prefix=f"/{settings.API_VERSION}/chat", tags=["chat"])
app.include_router(permits_router, prefix=f"/{settings.API_VERSION}/permits", tags=["permits"])
app.include_router(inspections_router, prefix=f"/{settings.API_VERSION}/inspections", tags=["inspections"])
app.include_router(projects_router, prefix=f"/{settings.API_VERSION}/projects", tags=["projects"])
app.include_router(clients_router, prefix=f"/{settings.API_VERSION}/clients", tags=["clients"])
app.include_router(documents_router, prefix=f"/{settings.API_VERSION}/documents", tags=["documents"])
app.include_router(quickbooks_router, prefix=f"/{settings.API_VERSION}/quickbooks", tags=["quickbooks"])
app.include_router(payments_router, prefix=f"/{settings.API_VERSION}/payments", tags=["payments"])
app.include_router(invoices_router, prefix=f"/{settings.API_VERSION}/invoices", tags=["invoices"])
app.include_router(site_visits_router, prefix=f"/{settings.API_VERSION}/site-visits", tags=["site-visits"])
app.include_router(jurisdictions_router, prefix=f"/{settings.API_VERSION}/jurisdictions", tags=["jurisdictions"])
app.include_router(users_router, prefix=f"/{settings.API_VERSION}/users", tags=["users"])

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
