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
            logger.warning("No service account credentials found in environment variables")
            
    except Exception as e:
        logger.error(f"Failed to create service account file: {e}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix=f"/{settings.API_VERSION}/chat", tags=["chat"])
app.include_router(permits_router, prefix=f"/{settings.API_VERSION}/permits", tags=["permits"])

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
        from app.services.google_service import google_service
        
        debug_info = {
            "service_account_file_exists": os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE),
            "service_account_file_path": settings.GOOGLE_SERVICE_ACCOUNT_FILE,
            "sheet_id": settings.SHEET_ID,
            "google_service_initialized": {
                "credentials": google_service.credentials is not None,
                "sheets_service": google_service.sheets_service is not None,
                "drive_service": google_service.drive_service is not None
            }
        }
        
        # Try to read the service account file if it exists
        if os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE):
            try:
                with open(settings.GOOGLE_SERVICE_ACCOUNT_FILE, 'r') as f:
                    creds = json.load(f)
                debug_info["service_account_info"] = {
                    "client_email": creds.get("client_email"),
                    "project_id": creds.get("project_id"),
                    "private_key_length": len(creds.get("private_key", "")),
                    "private_key_starts_correctly": creds.get("private_key", "").startswith("-----BEGIN PRIVATE KEY-----"),
                    "private_key_ends_correctly": creds.get("private_key", "").endswith("-----END PRIVATE KEY-----")
                }
            except Exception as e:
                debug_info["service_account_file_error"] = str(e)
        
        return debug_info
        
    except Exception as e:
        logger.error(f"Debug check failed: {e}")
        return {"error": str(e)}

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