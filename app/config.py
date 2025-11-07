import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    SHEET_ID: str = os.getenv("SHEET_ID", "")
    GOOGLE_SERVICE_ACCOUNT_FILE: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service-account.json")
    CHAT_WEBHOOK_URL: str = os.getenv("CHAT_WEBHOOK_URL", "")
    
    # QuickBooks Configuration
    QB_CLIENT_ID: str = os.getenv("QB_CLIENT_ID", "")
    QB_CLIENT_SECRET: str = os.getenv("QB_CLIENT_SECRET", "")
    QB_REDIRECT_URI: str = os.getenv("QB_REDIRECT_URI", "http://localhost:8000/v1/quickbooks/callback")
    QB_ENVIRONMENT: str = os.getenv("QB_ENVIRONMENT", "sandbox")  # "sandbox" or "production"
    
    # API Configuration
    API_VERSION: str = "v1"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS Settings - Allow all Cloudflare Pages deployments
    ALLOWED_ORIGINS: list = [
        "https://portal.houserenovatorsllc.com",
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "https://house-renovators-pwa.pages.dev",  # Cloudflare Pages
    ]
    
    # Regex pattern for Cloudflare Pages
    CLOUDFLARE_PAGES_PATTERN: str = r"https://.*\.house-renovators-ai-portal\.pages\.dev"
    
    # Dynamic CORS check for Cloudflare Pages deployments
    @staticmethod
    def is_allowed_origin(origin: str) -> bool:
        """Check if an origin is allowed, including dynamic Cloudflare Pages domains"""
        static_origins = [
            "https://portal.houserenovatorsllc.com",
            "http://localhost:3000",
            "http://localhost:5173",
            "https://house-renovators-pwa.pages.dev",
            "https://house-renovators-ai-portal.pages.dev",  # Main Cloudflare Pages domain
        ]
        
        if origin in static_origins:
            return True
            
        # Allow any Cloudflare Pages deployment of our project (subdomains)
        if origin and origin.endswith(".house-renovators-ai-portal.pages.dev"):
            return True
            
        return False

settings = Settings()
