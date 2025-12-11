"""
Test Permit API Endpoints (Phase B.1)

Tests the new PostgreSQL-backed permit endpoints.
"""

import asyncio
import sys
import requests
from datetime import datetime

API_BASE = "http://localhost:8000"
TOKEN = None  # Will be set after login


def login():
    """Login to get JWT token"""
    response = requests.post(
        f"{API_BASE}/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "admin123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        global TOKEN
        TOKEN = data["access_token"]
        print("✅ Logged in successfully")
        return True
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return False


def get_headers():
    """Get authorization headers"""
    return {"Authorization": f"Bearer {TOKEN}"}


def test_create_permit():
    """Test POST /v1/permits"""
    print("\n" + "="*80)
    print("TEST 1: Create Permit")
    print("="*80)
    
    # First get a project ID
    response = requests.get(
        f"{API_BASE}/v1/projects",
        headers=get_headers()
    )
    
    if response.status_code != 200 or not response.json():
        print("❌ No projects found - run project creation first")
        return None
    
    project = response.json()[0]
    project_id = project["id"]
    print(f"Using project: {project['business_id']} - {project['name']}")
    
    # Create permit
    response = requests.post(
        f"{API_BASE}/v1/permits",
        headers=get_headers(),
        json={
            "project_id": project_id,
            "permit_type": "Building",
            "jurisdiction": "City of Burnsville",
            "notes": "Re-roofing permit for Phase B.1 testing"
        }
    )
    
    if response.status_code == 201:
        permit = response.json()
        print(f"✅ Created permit: {permit['business_id']}")
        print(f"   - Type: {permit['permit_type']}")
        print(f"   - Status: {permit['status']}")
        print(f"   - Jurisdiction: {permit['jurisdiction']}")
        return permit
    else:
        print(f"❌ Failed to create permit: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_list_permits():
    """Test GET /v1/permits"""
    print("\n" + "="*80)
    print("TEST 2: List Permits")
    print("="*80)
    
    response = requests.get(
        f"{API_BASE}/v1/permits",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        permits = response.json()
        print(f"✅ Retrieved {len(permits)} permits")
        for permit in permits[:3]:  # Show first 3
            print(f"   - {permit['business_id']}: {permit['permit_type']} ({permit['status']})")
        return permits
    else:
        print(f"❌ Failed to list permits: {response.status_code}")
        print(f"   {response.text}")
        return []


def test_get_permit_by_business_id(business_id):
    """Test GET /v1/permits/by-business-id/{business_id}"""
    print("\n" + "="*80)
    print("TEST 3: Get Permit by Business ID")
    print("="*80)
    
    response = requests.get(
        f"{API_BASE}/v1/permits/by-business-id/{business_id}",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        permit = response.json()
        print(f"✅ Retrieved permit: {permit['business_id']}")
        print(f"   - Type: {permit['permit_type']}")
        print(f"   - Status: {permit['status']}")
        print(f"   - Created: {permit['created_at']}")
        return permit
    else:
        print(f"❌ Failed to get permit: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_update_permit(permit_id):
    """Test PUT /v1/permits/{id}"""
    print("\n" + "="*80)
    print("TEST 4: Update Permit")
    print("="*80)
    
    response = requests.put(
        f"{API_BASE}/v1/permits/{permit_id}",
        headers=get_headers(),
        json={
            "permit_number": "2025-BLD-TEST-001",
            "issuing_authority": "City of Burnsville Building Department",
            "inspector_name": "John Smith"
        }
    )
    
    if response.status_code == 200:
        permit = response.json()
        print(f"✅ Updated permit: {permit['business_id']}")
        print(f"   - Permit Number: {permit['permit_number']}")
        print(f"   - Issuing Authority: {permit['issuing_authority']}")
        print(f"   - Inspector: {permit['inspector_name']}")
        return permit
    else:
        print(f"❌ Failed to update permit: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_submit_permit(permit_id):
    """Test POST /v1/permits/{id}/submit"""
    print("\n" + "="*80)
    print("TEST 5: Submit Permit")
    print("="*80)
    
    response = requests.post(
        f"{API_BASE}/v1/permits/{permit_id}/submit",
        headers=get_headers(),
        json={
            "notes": "Permit submitted for review via API test"
        }
    )
    
    if response.status_code == 200:
        permit = response.json()
        print(f"✅ Submitted permit: {permit['business_id']}")
        print(f"   - Old Status: Draft")
        print(f"   - New Status: {permit['status']}")
        print(f"   - Application Date: {permit['application_date']}")
        return permit
    else:
        print(f"❌ Failed to submit permit: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_update_status(permit_id):
    """Test PUT /v1/permits/{id}/status"""
    print("\n" + "="*80)
    print("TEST 6: Update Permit Status")
    print("="*80)
    
    response = requests.put(
        f"{API_BASE}/v1/permits/{permit_id}/status",
        headers=get_headers(),
        json={
            "status": "Approved",
            "notes": "Approved after review - all requirements met"
        }
    )
    
    if response.status_code == 200:
        permit = response.json()
        print(f"✅ Updated permit status: {permit['business_id']}")
        print(f"   - New Status: {permit['status']}")
        print(f"   - Approved At: {permit['approved_at']}")
        return permit
    else:
        print(f"❌ Failed to update status: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_precheck(permit_id):
    """Test GET /v1/permits/{id}/precheck"""
    print("\n" + "="*80)
    print("TEST 7: Permit Precheck")
    print("="*80)
    
    response = requests.get(
        f"{API_BASE}/v1/permits/{permit_id}/precheck",
        params={"inspection_type": "Foundation"},
        headers=get_headers()
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Precheck completed")
        print(f"   - Can Schedule: {result['can_schedule']}")
        print(f"   - AI Confidence: {result['ai_confidence']}")
        if result['missing']:
            print(f"   - Missing Requirements:")
            for item in result['missing']:
                print(f"     • {item}")
        if result['warnings']:
            print(f"   - Warnings:")
            for warning in result['warnings']:
                print(f"     • {warning}")
        return result
    else:
        print(f"❌ Failed to run precheck: {response.status_code}")
        print(f"   {response.text}")
        return None


def main():
    """Run all permit API tests"""
    print("="*80)
    print("PERMIT API TESTS - PHASE B.1")
    print("="*80)
    print()
    print("Ensure backend is running: python -m uvicorn app.main:app --reload")
    print()
    
    # Login
    if not login():
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Test 1: Create permit
    permit = test_create_permit()
    if not permit:
        print("\n❌ Tests failed - cannot create permit")
        return
    
    permit_id = permit["id"]
    business_id = permit["business_id"]
    
    # Test 2: List permits
    test_list_permits()
    
    # Test 3: Get by business ID
    test_get_permit_by_business_id(business_id)
    
    # Test 4: Update permit
    test_update_permit(permit_id)
    
    # Test 5: Submit permit
    test_submit_permit(permit_id)
    
    # Test 6: Update status to Approved
    test_update_status(permit_id)
    
    # Test 7: Run precheck
    test_precheck(permit_id)
    
    print("\n" + "="*80)
    print("✅ ALL PERMIT API TESTS COMPLETE")
    print("="*80)
    print()
    print(f"Test Permit Created: {business_id}")
    print()


if __name__ == "__main__":
    main()
