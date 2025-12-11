import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        self.SHEET_ID: str = os.getenv("SHEET_ID", "")
        self.GOOGLE_SERVICE_ACCOUNT_FILE: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service-account.json")
        self.CHAT_WEBHOOK_URL: str = os.getenv("CHAT_WEBHOOK_URL", "")
        
        # QuickBooks Configuration
        self.QB_CLIENT_ID: str = os.getenv("QB_CLIENT_ID", "")
        self.QB_CLIENT_SECRET: str = os.getenv("QB_CLIENT_SECRET", "")
        self.QB_REDIRECT_URI: str = os.getenv("QB_REDIRECT_URI", "http://localhost:8000/v1/quickbooks/callback")
        self.QB_ENVIRONMENT: str = os.getenv("QB_ENVIRONMENT", "sandbox")  # "sandbox" or "production"
        
        # Database Configuration
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/houserenovators")
        self.REDIS_URL: str = os.getenv("REDIS_URL", "")  # Optional: redis://localhost:6379/0
        
        # Feature Flags
        self.ENABLE_DB_BACKEND: bool = os.getenv("ENABLE_DB_BACKEND", "false").lower() == "true"
        self.DB_READ_FALLBACK: bool = os.getenv("DB_READ_FALLBACK", "true").lower() == "true"  # Fallback to Sheets if DB fails
        self.ENABLE_AI: bool = os.getenv("ENABLE_AI", "true").lower() == "true"
        
        # AI Configuration
        self.OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.OPENAI_PROMPT_STYLE: str = os.getenv("OPENAI_PROMPT_STYLE", "conversational")  # conversational, technical, concise
        self.AI_STRICT_MODE: bool = os.getenv("AI_STRICT_MODE", "false").lower() == "true"  # Strict function calling validation
        
        # API Configuration
        self.API_VERSION: str = "v1"
        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")  # development, staging, production
        
        # CORS Settings - Allow all Cloudflare Pages deployments
        self.ALLOWED_ORIGINS: list = [
            "https://portal.houserenovatorsllc.com",
            "http://localhost:3000",
            "http://localhost:5173",  # Vite dev server
            "https://house-renovators-pwa.pages.dev",  # Cloudflare Pages
            "https://houserenoai.pages.dev",  # Cloudflare Pages (current)
        ]
        
        # Regex pattern for Cloudflare Pages
        self.CLOUDFLARE_PAGES_PATTERN: str = r"https://.*\.(house-renovators-ai-portal|houserenoai)\.pages\.dev"
    
    # Dynamic CORS check for Cloudflare Pages deployments
    @staticmethod
    def is_allowed_origin(origin: str) -> bool:
        """Check if an origin is allowed, including dynamic Cloudflare Pages domains"""
        static_origins = [
            "https://portal.houserenovatorsllc.com",
            "http://localhost:3000",
            "http://localhost:5173",
            "https://house-renovators-pwa.pages.dev",
            "https://house-renovators-ai-portal.pages.dev",  # Old Cloudflare Pages domain
            "https://houserenoai.pages.dev",  # Current Cloudflare Pages domain
        ]
        
        if origin in static_origins:
            return True
            
        # Allow any Cloudflare Pages deployment of our projects (subdomains)
        if origin and (origin.endswith(".house-renovators-ai-portal.pages.dev") or origin.endswith(".houserenoai.pages.dev")):
            return True
            
        return False

settings = Settings()
