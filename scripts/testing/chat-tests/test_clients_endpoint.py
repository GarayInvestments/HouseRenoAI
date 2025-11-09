"""
Test the clients endpoint directly
"""
import asyncio
import sys
from dotenv import load_dotenv

sys.path.insert(0, '.')
load_dotenv()

from app.routes.clients import get_all_clients
from app.services import google_service as google_service_module
from app.services.google_service import GoogleService

async def test_endpoint():
    print("\n" + "="*60)
    print("TESTING /v1/clients ENDPOINT")
    print("="*60)
    
    # Initialize the service (simulating app startup)
    google_service_module.google_service = GoogleService()
    google_service_module.google_service.initialize()
    print("✓ Google service initialized")
    
    # Call the endpoint
    print("\n--- Calling get_all_clients() ---")
    try:
        result = await get_all_clients()
        print(f"✓ Endpoint returned {len(result)} items")
        
        if result:
            print(f"\nFirst item keys: {list(result[0].keys())}")
            print(f"\nFirst 3 items:")
            for i, item in enumerate(result[:3]):
                client_id = item.get('Client ID', 'N/A')
                name = item.get('Full Name', item.get('Client Name', 'N/A'))
                print(f"  {i+1}. ID: {client_id}, Name: {name}")
        else:
            print("⚠ No items returned!")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(test_endpoint())
