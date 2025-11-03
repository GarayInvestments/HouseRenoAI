import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    SHEET_ID: str = os.getenv("SHEET_ID", "")
    GOOGLE_SERVICE_ACCOUNT_FILE: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service-account.json")
    CHAT_WEBHOOK_URL: str = os.getenv("CHAT_WEBHOOK_URL", "")
    
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
    
<<<<<<< HEAD
    # Dynamic CORS check for Cloudflare Pages deployments
    @staticmethod
    def is_allowed_origin(origin: str) -> bool:
        """Check if an origin is allowed, including dynamic Cloudflare Pages domains"""
        static_origins = [
            "https://portal.houserenovatorsllc.com",
            "http://localhost:3000",
            "http://localhost:5173",
            "https://house-renovators-pwa.pages.dev",
        ]
        
        if origin in static_origins:
            return True
            
        # Allow any Cloudflare Pages deployment of our project
        if origin and origin.endswith(".house-renovators-ai-portal.pages.dev"):
            return True
            
        return False
=======
    # Regex pattern for Cloudflare Pages
    CLOUDFLARE_PAGES_PATTERN: str = r"https://.*\.house-renovators-ai-portal\.pages\.dev"
>>>>>>> d2d04290c3e061cb48cfda724eca6252d77eeec3

settings = Settings()
