import asyncio
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, '.')

# Load environment variables from .env file
load_dotenv()

from app.services.google_service import GoogleService

async def test_clients():
    print("\n" + "="*60)
    print("CLIENTS DATA DEBUGGING")
    print("="*60)
    
    # Initialize service
    service = GoogleService()
    try:
        service.initialize()
        print("✓ Google service initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return
    
    # Test 1: Get clients data
    print("\n--- Test 1: get_clients_data() ---")
    try:
        clients = await service.get_clients_data()
        print(f"✓ Retrieved {len(clients)} clients")
        
        if clients:
            print(f"\nFirst client keys: {list(clients[0].keys())}")
            print(f"First client sample data:")
            for key, value in list(clients[0].items())[:5]:
                print(f"  {key}: {value}")
            
            if len(clients) > 1:
                print(f"\nSecond client ID: {clients[1].get('Client ID', 'N/A')}")
                print(f"Second client Name: {clients[1].get('Client Name', clients[1].get('Full Name', 'N/A'))}")
        else:
            print("⚠ No clients returned!")
            
    except Exception as e:
        print(f"✗ Error getting clients: {e}")
    
    # Test 2: Get projects data for comparison
    print("\n--- Test 2: get_projects_data() for comparison ---")
    try:
        projects = await service.get_projects_data()
        print(f"✓ Retrieved {len(projects)} projects")
        
        if projects:
            print(f"\nFirst project keys: {list(projects[0].keys())}")
            
            # Extract unique client IDs from projects
            client_ids = set()
            for proj in projects:
                cid = proj.get('Client ID', '')
                if cid:
                    client_ids.add(cid)
            print(f"\nUnique Client IDs in projects: {len(client_ids)}")
            print(f"Client IDs: {sorted(client_ids)}")
    except Exception as e:
        print(f"✗ Error getting projects: {e}")
    
    # Test 3: Check cache
    print("\n--- Test 3: Cache inspection ---")
    print(f"Cache keys: {list(service._cache.keys())}")
    if 'clients_data' in service._cache:
        cached_data = service._cache['clients_data']['data']
        print(f"Cached clients count: {len(cached_data)}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(test_clients())
