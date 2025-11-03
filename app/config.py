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
    
    # CORS Settings
    ALLOWED_ORIGINS: list = [
        "https://portal.houserenovatorsllc.com",
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "https://house-renovators-pwa.pages.dev"  # Cloudflare Pages
    ]

settings = Settings()