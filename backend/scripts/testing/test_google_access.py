#!/usr/bin/env python3
"""
Test Google Sheets Access from Backend
Verifies the backend can connect and access all sheets
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv()

from app.services.google_service import GoogleService
from app.config import settings

async def test_google_access():
    """Test access to Google Sheets"""
    print("🏠 House Renovators AI - Backend Google Sheets Access Test")
    print("="*80)
    
    # Show configuration
    print("\n📋 Configuration:")
    print(f"   Sheet ID: {settings.SHEET_ID}")
    print(f"   Service Account File: {settings.GOOGLE_SERVICE_ACCOUNT_FILE}")
    print(f"   OpenAI API Key: {'✅ Set' if settings.OPENAI_API_KEY else '❌ Missing'}")
    
    # Check if service account file exists
    service_account_path = Path(settings.GOOGLE_SERVICE_ACCOUNT_FILE)
    if not service_account_path.is_absolute():
        service_account_path = backend_dir / service_account_path
    
    print(f"\n📁 Service Account File:")
    print(f"   Path: {service_account_path}")
    print(f"   Exists: {'✅ Yes' if service_account_path.exists() else '❌ No'}")
    
    if not service_account_path.exists():
        print("\n❌ ERROR: Service account file not found!")
        return False
    
    # Initialize Google Service
    print("\n🔧 Initializing Google Service...")
    google_service = GoogleService()
    google_service.initialize()
    
    if not google_service.sheets_service:
        print("❌ ERROR: Failed to initialize Google Sheets service")
        return False
    
    print("✅ Google Sheets service initialized")
    
    # Test access to each sheet
    sheets_to_test = [
        "Clients",
        "Projects",
        "Permits",
        "Site Visits",
        "Subcontractors",
        "Documents",
        "Tasks",
        "Payments",
        "Jurisdiction",
        "Inspectors",
        "Construction Phase Tracking",
        "Phase Tracking Images"
    ]
    
    print("\n" + "="*80)
    print("🔍 Testing Sheet Access")
    print("="*80)
    
    all_success = True
    
    for sheet_name in sheets_to_test:
        try:
            print(f"\n📄 {sheet_name}...")
            
            # Read first 3 rows (headers + 2 data rows)
            data = await google_service.read_sheet_data(f"'{sheet_name}'!A1:Z3")
            
            if data:
                headers = data[0] if len(data) > 0 else []
                row_count = len(data) - 1  # Subtract header row
                
                print(f"   ✅ Access successful")
                print(f"   📊 Columns: {len(headers)}")
                print(f"   📝 Data rows (sample): {row_count}")
                
                if headers:
                    print(f"   📋 Headers: {', '.join(headers[:5])}")
                    if len(headers) > 5:
                        print(f"                ...and {len(headers) - 5} more")
            else:
                print(f"   ⚠️  Sheet exists but is empty")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            all_success = False
    
    # Test specific data retrieval methods
    print("\n" + "="*80)
    print("🧪 Testing Data Retrieval Methods")
    print("="*80)
    
    try:
        print("\n📊 Testing get_clients_data()...")
        clients = await google_service.get_clients_data()
        print(f"   ✅ Retrieved {len(clients)} clients")
        if clients:
            print(f"   📋 Sample client keys: {list(clients[0].keys())[:5]}")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        all_success = False
    
    try:
        print("\n📊 Testing get_projects_data()...")
        projects = await google_service.get_projects_data()
        print(f"   ✅ Retrieved {len(projects)} projects")
        if projects:
            print(f"   📋 Sample project keys: {list(projects[0].keys())[:5]}")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        all_success = False
    
    try:
        print("\n📊 Testing get_permits_data()...")
        permits = await google_service.get_permits_data()
        print(f"   ✅ Retrieved {len(permits)} permits")
        if permits:
            print(f"   📋 Sample permit keys: {list(permits[0].keys())[:5]}")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        all_success = False
    
    # Final summary
    print("\n" + "="*80)
    if all_success:
        print("✅ ALL TESTS PASSED: Backend has full access to Google Sheets!")
    else:
        print("⚠️  SOME TESTS FAILED: Check errors above")
    print("="*80)
    
    return all_success

if __name__ == "__main__":
    success = asyncio.run(test_google_access())
    sys.exit(0 if success else 1)
