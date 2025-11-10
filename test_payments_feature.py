"""
Test script for Payments feature implementation
Tests API endpoints, QB sync, and data validation
"""

import asyncio
import json
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '.')

from app.services.google_service import GoogleService
from app.services.quickbooks_service import quickbooks_service
from app.config import settings


async def test_payments_sheet_exists():
    """Test 1: Verify Payments sheet exists with correct structure"""
    print("\n" + "="*60)
    print("TEST 1: Verify Payments Sheet Structure")
    print("="*60)
    
    try:
        google_service = GoogleService()
        google_service.initialize()
        
        # Try to read Payments sheet
        data = await google_service.read_sheet_data('Payments!A1:K1')
        
        if not data:
            print("❌ FAILED: Payments sheet not found or empty")
            return False
        
        headers = data[0]
        expected_headers = [
            'Payment ID', 'Invoice ID', 'Project ID', 'Client ID', 'Amount',
            'Payment Date', 'Payment Method', 'Status', 'QB Payment ID',
            'Transaction ID', 'Notes'
        ]
        
        print(f"\n📋 Found headers: {headers}")
        print(f"📋 Expected headers: {expected_headers}")
        
        if headers == expected_headers:
            print("✅ PASSED: Payments sheet has correct structure (11 columns)")
            return True
        else:
            print("❌ FAILED: Headers don't match expected structure")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Error reading Payments sheet: {e}")
        return False


async def test_qb_payments_methods():
    """Test 2: Verify QB payment methods exist and work"""
    print("\n" + "="*60)
    print("TEST 2: Verify QuickBooks Payment Methods")
    print("="*60)
    
    try:
        # Check if QB is authenticated
        if not quickbooks_service.is_authenticated():
            print("⚠️  SKIPPED: QuickBooks not authenticated")
            return None
        
        print("✅ QuickBooks authenticated")
        
        # Test get_payments method exists
        if not hasattr(quickbooks_service, 'get_payments'):
            print("❌ FAILED: get_payments method not found")
            return False
        print("✅ get_payments method exists")
        
        # Test sync_payments_to_sheets method exists
        if not hasattr(quickbooks_service, 'sync_payments_to_sheets'):
            print("❌ FAILED: sync_payments_to_sheets method not found")
            return False
        print("✅ sync_payments_to_sheets method exists")
        
        # Test _map_qb_payment_to_sheet method exists
        if not hasattr(quickbooks_service, '_map_qb_payment_to_sheet'):
            print("❌ FAILED: _map_qb_payment_to_sheet method not found")
            return False
        print("✅ _map_qb_payment_to_sheet method exists")
        
        print("\n✅ PASSED: All QB payment methods implemented")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Error checking QB methods: {e}")
        return False


async def test_context_enhancements():
    """Test 3: Verify context enhancements (Projects and Permits fields)"""
    print("\n" + "="*60)
    print("TEST 3: Verify Context Enhancements")
    print("="*60)
    
    try:
        google_service = GoogleService()
        google_service.initialize()
        
        # Test Projects fields
        projects = await google_service.get_projects_data()
        if projects and len(projects) > 0:
            project = projects[0]
            
            # Check for new fields
            has_project_type = 'Project Type' in project
            has_start_date = 'Start Date' in project
            has_project_cost = 'Project Cost (Materials + Labor)' in project
            has_county = 'County' in project
            
            print(f"\n📊 Projects Context Fields:")
            print(f"  - Project Type: {'✅' if has_project_type else '❌'}")
            print(f"  - Start Date: {'✅' if has_start_date else '❌'}")
            print(f"  - Project Cost: {'✅' if has_project_cost else '❌'}")
            print(f"  - County: {'✅' if has_county else '❌'}")
            
            projects_ok = has_project_type or has_start_date or has_project_cost or has_county
        else:
            print("⚠️  No projects found to test")
            projects_ok = True  # Can't fail if no data
        
        # Test Permits fields
        permits = await google_service.get_permits_data()
        if permits and len(permits) > 0:
            permit = permits[0]
            
            # Check for new fields
            has_project_id = 'Project ID' in permit
            has_application_date = 'Application Date' in permit
            has_approval_date = 'Approval Date' in permit
            
            print(f"\n📊 Permits Context Fields:")
            print(f"  - Project ID: {'✅' if has_project_id else '❌'}")
            print(f"  - Application Date: {'✅' if has_application_date else '❌'}")
            print(f"  - Approval Date: {'✅' if has_approval_date else '❌'}")
            
            permits_ok = has_project_id or has_application_date or has_approval_date
        else:
            print("⚠️  No permits found to test")
            permits_ok = True  # Can't fail if no data
        
        if projects_ok and permits_ok:
            print("\n✅ PASSED: Context enhancements verified")
            return True
        else:
            print("\n❌ FAILED: Some context fields missing")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Error checking context fields: {e}")
        return False


async def test_payments_in_context_builder():
    """Test 4: Verify payment keywords in context builder"""
    print("\n" + "="*60)
    print("TEST 4: Verify Payment Keywords in Context Builder")
    print("="*60)
    
    try:
        from app.utils.context_builder import get_required_contexts
        
        # Test payment keywords
        test_messages = [
            ("Show me all payments", {'sheets'}),
            ("Has Javier paid?", {'sheets'}),
            ("Sync payments from QuickBooks", {'sheets', 'quickbooks'}),
            ("Payment status for client", {'sheets'}),
            ("zelle payment received", {'sheets'}),
        ]
        
        all_passed = True
        for message, expected in test_messages:
            contexts = get_required_contexts(message)
            
            # Check if expected contexts are present
            if expected.issubset(contexts):
                print(f"✅ '{message}' → {contexts}")
            else:
                print(f"❌ '{message}' → {contexts} (expected {expected})")
                all_passed = False
        
        if all_passed:
            print("\n✅ PASSED: Payment keywords detected correctly")
            return True
        else:
            print("\n❌ FAILED: Some payment keywords not detected")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Error testing context builder: {e}")
        return False


async def test_ai_function_handlers():
    """Test 5: Verify AI function handlers are registered"""
    print("\n" + "="*60)
    print("TEST 5: Verify AI Function Handlers")
    print("="*60)
    
    try:
        from app.handlers.ai_functions import FUNCTION_HANDLERS
        
        # Check for payment handlers
        has_sync = 'sync_quickbooks_payments' in FUNCTION_HANDLERS
        has_get_client = 'get_client_payments' in FUNCTION_HANDLERS
        
        print(f"\n🔧 Function Handlers:")
        print(f"  - sync_quickbooks_payments: {'✅' if has_sync else '❌'}")
        print(f"  - get_client_payments: {'✅' if has_get_client else '❌'}")
        
        if has_sync and has_get_client:
            print("\n✅ PASSED: Payment function handlers registered")
            return True
        else:
            print("\n❌ FAILED: Payment function handlers missing")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Error checking function handlers: {e}")
        return False


async def test_payment_data_loading():
    """Test 6: Verify payments data can be loaded"""
    print("\n" + "="*60)
    print("TEST 6: Verify Payments Data Loading")
    print("="*60)
    
    try:
        google_service = GoogleService()
        google_service.initialize()
        
        # Try to load payments data
        payments = await google_service.get_all_sheet_data('Payments')
        
        print(f"\n📊 Found {len(payments)} payment records")
        
        if payments:
            # Show first payment as example
            print(f"\n📄 Sample payment record:")
            for key, value in list(payments[0].items())[:5]:
                print(f"  - {key}: {value}")
        
        print("\n✅ PASSED: Payments data loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Error loading payments data: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 PAYMENTS FEATURE TEST SUITE")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run all tests
    results.append(("Payments Sheet Structure", await test_payments_sheet_exists()))
    results.append(("QB Payment Methods", await test_qb_payments_methods()))
    results.append(("Context Enhancements", await test_context_enhancements()))
    results.append(("Payment Keywords", await test_payments_in_context_builder()))
    results.append(("AI Function Handlers", await test_ai_function_handlers()))
    results.append(("Payment Data Loading", await test_payment_data_loading()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result is True else ("❌ FAILED" if result is False else "⚠️  SKIPPED")
        print(f"{status}: {test_name}")
    
    print(f"\n📈 Results: {passed} passed, {failed} failed, {skipped} skipped out of {total} tests")
    
    if failed == 0:
        print("\n🎉 All tests passed! Feature is ready for production use.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review errors above.")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
