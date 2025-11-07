"""
Authentication service for House Renovators AI Portal
Handles user authentication, JWT tokens, and password hashing
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from app.config import settings
import app.services.google_service as google_service_module
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.OPENAI_API_KEY  # Using existing secret, but should have dedicated secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

class AuthService:
    """Handle authentication operations"""
    
    USERS_SHEET = "Users"
    
    def __init__(self):
        """Initialize auth service"""
        # Don't create sheet during init, only when needed
        pass
    
    def ensure_users_sheet_exists(self):
        """Create Users sheet if it doesn't exist"""
        try:
            google_service = google_service_module.google_service
            if not google_service or not google_service.sheets_service:
                logger.warning("Google service not initialized, cannot create Users sheet")
                return
            
            # Try to read from Users sheet
            try:
                google_service.sheets_service.spreadsheets().values().get(
                    spreadsheetId=settings.SHEET_ID,
                    range=f"{self.USERS_SHEET}!A1:F1"
                ).execute()
                logger.info("Users sheet already exists")
            except Exception:
                # Sheet doesn't exist, create it
                logger.info("Creating Users sheet...")
                
                # Create sheet
                requests = [{
                    "addSheet": {
                        "properties": {
                            "title": self.USERS_SHEET,
                            "gridProperties": {
                                "rowCount": 100,
                                "columnCount": 6
                            }
                        }
                    }
                }]
                
                google_service.sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=settings.SHEET_ID,
                    body={"requests": requests}
                ).execute()
                
                # Add headers
                headers = [["Email", "Password Hash", "Name", "Role", "Created At", "Last Login"]]
                google_service.sheets_service.spreadsheets().values().update(
                    spreadsheetId=settings.SHEET_ID,
                    range=f"{self.USERS_SHEET}!A1:F1",
                    valueInputOption="RAW",
                    body={"values": headers}
                ).execute()
                
                logger.info("Users sheet created successfully")
                
        except Exception as e:
            logger.error(f"Error ensuring Users sheet exists: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash a password (bcrypt has 72 byte limit)"""
        # Bcrypt only accepts passwords up to 72 bytes
        # Truncate the password if it's longer
        if len(password.encode('utf-8')) > 72:
            password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        # Bcrypt only accepts passwords up to 72 bytes
        # Truncate the password if it's longer
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, email: str, role: str = "user") -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        to_encode = {
            "sub": email,
            "role": role,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email from Google Sheets"""
        try:
            google_service = google_service_module.google_service
            if not google_service or not google_service.sheets_service:
                logger.error("Google service not initialized")
                return None
            
            # Read all users
            result = google_service.sheets_service.spreadsheets().values().get(
                spreadsheetId=settings.SHEET_ID,
                range=f"{self.USERS_SHEET}!A2:F1000"
            ).execute()
            
            rows = result.get('values', [])
            
            for row in rows:
                if len(row) > 0 and row[0].lower() == email.lower():
                    return {
                        "email": row[0],
                        "password_hash": row[1] if len(row) > 1 else "",
                        "name": row[2] if len(row) > 2 else "",
                        "role": row[3] if len(row) > 3 else "user",
                        "created_at": row[4] if len(row) > 4 else "",
                        "last_login": row[5] if len(row) > 5 else ""
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    async def create_user(self, email: str, password: str, name: str, role: str = "user") -> bool:
        """Create new user in Google Sheets"""
        try:
            google_service = google_service_module.google_service
            if not google_service or not google_service.sheets_service:
                logger.error("Google service not initialized")
                return False
            
            # Check if user already exists
            existing_user = await self.get_user_by_email(email)
            if existing_user:
                logger.warning(f"User {email} already exists")
                return False
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Create user row
            now = datetime.utcnow().isoformat()
            user_row = [[email, password_hash, name, role, now, ""]]
            
            # Append to sheet
            google_service.sheets_service.spreadsheets().values().append(
                spreadsheetId=settings.SHEET_ID,
                range=f"{self.USERS_SHEET}!A:F",
                valueInputOption="RAW",
                body={"values": user_row}
            ).execute()
            
            logger.info(f"User {email} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate user and return user info if valid"""
        user = await self.get_user_by_email(email)
        
        if not user:
            logger.warning(f"User {email} not found")
            return None
        
        if not self.verify_password(password, user["password_hash"]):
            logger.warning(f"Invalid password for user {email}")
            return None
        
        # Update last login
        try:
            await self.update_last_login(email)
        except Exception as e:
            logger.warning(f"Failed to update last login: {e}")
        
        return user
    
    async def update_last_login(self, email: str):
        """Update last login timestamp for user"""
        try:
            google_service = google_service_module.google_service
            if not google_service or not google_service.sheets_service:
                return
            
            # Find user row
            result = google_service.sheets_service.spreadsheets().values().get(
                spreadsheetId=settings.SHEET_ID,
                range=f"{self.USERS_SHEET}!A2:F1000"
            ).execute()
            
            rows = result.get('values', [])
            
            for idx, row in enumerate(rows):
                if len(row) > 0 and row[0].lower() == email.lower():
                    # Update last login (row index + 2 because of header and 0-based index)
                    row_num = idx + 2
                    now = datetime.utcnow().isoformat()
                    
                    google_service.sheets_service.spreadsheets().values().update(
                        spreadsheetId=settings.SHEET_ID,
                        range=f"{self.USERS_SHEET}!F{row_num}",
                        valueInputOption="RAW",
                        body={"values": [[now]]}
                    ).execute()
                    
                    break
                    
        except Exception as e:
            logger.error(f"Error updating last login: {e}")

# Global auth service instance
auth_service = AuthService()
