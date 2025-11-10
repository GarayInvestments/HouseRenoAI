#!/usr/bin/env python3
"""Check what columns exist in Clients sheet"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services import google_service as google_service_module

async def main():
    google_service = google_service_module.google_service
    
    if not google_service:
        print("ERROR: Google service not initialized")
        return
    
    clients = await google_service.get_clients_data()
    
    if clients:
        print(f"\n✅ Found {len(clients)} clients")
        print(f"\n📋 Available columns in Clients sheet:")
        print("-" * 60)
        for key in clients[0].keys():
            print(f"  - {key}")
        
        print(f"\n📧 Sample client data (first client):")
        print("-" * 60)
        for key, value in clients[0].items():
            if key.lower() in ['email', 'phone', 'full name', 'client id', 'client name']:
                print(f"  {key}: {value}")
    else:
        print("❌ No clients found")

if __name__ == "__main__":
    asyncio.run(main())
