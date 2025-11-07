"""
Create initial admin user for House Renovators AI Portal
Usage: python scripts/create_admin_user.py
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.auth_service import auth_service
import app.services.google_service as google_service_module
from app.services.google_service import GoogleService
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_admin():
    """Create initial admin user"""
    try:
        # Initialize Google service
        logger.info("Initializing Google service...")
        google_service_module.google_service = GoogleService()
        google_service_module.google_service.initialize()
        
        # Ensure Users sheet exists
        logger.info("Ensuring Users sheet exists...")
        auth_service.ensure_users_sheet_exists()
        
        # Get admin credentials
        print("\n=== Create Initial Admin User ===\n")
        email = input("Enter admin email: ").strip()
        name = input("Enter admin name: ").strip()
        password = input("Enter admin password: ").strip()
        
        if not email or not name or not password:
            print("Error: All fields are required")
            return
        
        # Check if user already exists
        existing_user = await auth_service.get_user_by_email(email)
        if existing_user:
            print(f"\nError: User {email} already exists!")
            return
        
        # Create admin user
        logger.info(f"Creating admin user: {email}")
        success = await auth_service.create_user(
            email=email,
            password=password,
            name=name,
            role="admin"
        )
        
        if success:
            print(f"\n✅ Admin user created successfully!")
            print(f"Email: {email}")
            print(f"Name: {name}")
            print(f"Role: admin")
            print(f"\nYou can now login with these credentials.")
        else:
            print("\n❌ Failed to create admin user")
            
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_admin())
