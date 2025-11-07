"""Quick script to create user steve@garayinvestments.com"""
import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.auth_service import auth_service
import app.services.google_service as google_service_module
from app.services.google_service import GoogleService

async def create():
    # Initialize Google service
    google_service_module.google_service = GoogleService()
    google_service_module.google_service.initialize()
    
    # Ensure Users sheet exists
    auth_service.ensure_users_sheet_exists()
    
    # Create user
    success = await auth_service.create_user(
        email='steve@garayinvestments.com',
        password='Stv060485!',
        name='Steve Garay',
        role='admin'
    )
    
    if success:
        print('✅ User steve@garayinvestments.com created successfully!')
    else:
        print('❌ User already exists or creation failed')

asyncio.run(create())
