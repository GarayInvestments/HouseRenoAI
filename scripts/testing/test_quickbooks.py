"""
QuickBooks Integration Test Script

Run this script to verify QuickBooks configuration and test the OAuth flow.
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.config import settings
from app.services.quickbooks_service import quickbooks_service


def test_configuration():
    """Test QuickBooks configuration"""
    print("🔧 Testing QuickBooks Configuration")
    print("=" * 50)
    
    # Check environment variables
    print(f"✓ QB_CLIENT_ID: {'SET' if settings.QB_CLIENT_ID else '❌ MISSING'}")
    print(f"✓ QB_CLIENT_SECRET: {'SET' if settings.QB_CLIENT_SECRET else '❌ MISSING'}")
    print(f"✓ QB_REDIRECT_URI: {settings.QB_REDIRECT_URI}")
    print(f"✓ QB_ENVIRONMENT: {settings.QB_ENVIRONMENT}")
    print()
    
    # Check service initialization
    print("✓ QuickBooksService initialized successfully")
    print(f"  - Base URL: {quickbooks_service.base_url}")
    print(f"  - Auth URL: {quickbooks_service.auth_url}")
    print(f"  - Token URL: {quickbooks_service.token_url}")
    print()
    
    # Check authentication status
    status = quickbooks_service.get_status()
    print("📊 Current Status:")
    print(f"  - Authenticated: {status['authenticated']}")
    print(f"  - Realm ID: {status['realm_id'] or 'Not set'}")
    print(f"  - Environment: {status['environment']}")
    print(f"  - Token Expires: {status['token_expires_at'] or 'Not set'}")
    print()
    
    # Generate auth URL
    auth_url = quickbooks_service.get_auth_url()
    print("🔐 OAuth2 Authorization URL:")
    print(f"  {auth_url}")
    print()
    
    print("✅ Configuration test complete!")
    print()
    print("📝 Next Steps:")
    print("1. Start the backend:")
    print("   python -m uvicorn app.main:app --reload --port 8000")
    print()
    print("2. Visit the auth URL:")
    print("   http://localhost:8000/v1/quickbooks/auth")
    print()
    print("3. Login to QuickBooks and authorize the app")
    print()
    print("4. Check status:")
    print("   http://localhost:8000/v1/quickbooks/status")
    print()
    print("5. Test API endpoints:")
    print("   http://localhost:8000/v1/quickbooks/customers")
    print("   http://localhost:8000/v1/quickbooks/invoices")


def main():
    """Main test function"""
    try:
        test_configuration()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
