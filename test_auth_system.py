"""
Quick test to verify the new authentication system is working.
Run this after completing the migration to ensure everything is set up correctly.
"""

import asyncio
from app.db.session import get_db
from app.services.auth_service_v2 import get_auth_service, get_token_service
from app.db.models import User

async def test_auth_system():
    print("=" * 60)
    print("🔐 Testing Modern Authentication System")
    print("=" * 60)
    
    # Get database session
    async for db in get_db():
        try:
            # Test 1: Token Service
            print("\n✅ Test 1: Token Service")
            token_service = get_token_service()
            
            # Create test access token
            test_token = token_service.create_access_token(
                user_id="test-user-id",
                email="test@example.com",
                role="admin"
            )
            print(f"   Created access token: {test_token[:50]}...")
            
            # Verify token
            payload = token_service.verify_access_token(test_token)
            print(f"   Token verified: {payload['email']}, Role: {payload['role']}")
            print(f"   Token expires in: {payload['exp']} seconds")
            
            # Test 2: Auth Service
            print("\n✅ Test 2: Auth Service")
            auth_service = get_auth_service(db)
            
            # Check if admin user exists
            admin_user = await auth_service.get_user_by_email("steve@houserenovatorsllc.com")
            if admin_user:
                print(f"   Found admin user: {admin_user.full_name}")
                print(f"   User ID: {admin_user.id}")
                print(f"   Role: {admin_user.role}")
            else:
                print("   ⚠️ Admin user not found - you may need to create one")
            
            # Test 3: Database Tables
            print("\n✅ Test 3: Database Tables")
            from sqlalchemy import text
            
            # Check refresh_tokens table
            result = await db.execute(text("SELECT COUNT(*) FROM refresh_tokens"))
            count = result.scalar()
            print(f"   refresh_tokens: {count} records")
            
            # Check token_blacklist table
            result = await db.execute(text("SELECT COUNT(*) FROM token_blacklist"))
            count = result.scalar()
            print(f"   token_blacklist: {count} records")
            
            # Check user_sessions table
            result = await db.execute(text("SELECT COUNT(*) FROM user_sessions"))
            count = result.scalar()
            print(f"   user_sessions: {count} records")
            
            # Check login_attempts table
            result = await db.execute(text("SELECT COUNT(*) FROM login_attempts"))
            count = result.scalar()
            print(f"   login_attempts: {count} records")
            
            # Test 4: Environment Variables
            print("\n✅ Test 4: Environment Variables")
            from app.config import settings
            
            if settings.JWT_SECRET:
                print(f"   JWT_SECRET: Set ({len(settings.JWT_SECRET)} chars)")
            else:
                print("   ⚠️ JWT_SECRET: Not set - using SUPABASE_JWT_SECRET as fallback")
            
            print(f"   JWT_ACCESS_TOKEN_EXPIRE_MINUTES: {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES}")
            print(f"   JWT_REFRESH_TOKEN_EXPIRE_DAYS: {settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS}")
            
            # Summary
            print("\n" + "=" * 60)
            print("✅ Authentication system test completed successfully!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Update app/main.py to use auth_v2 routes")
            print("2. Update frontend to handle refresh tokens")
            print("3. Test login flow with real credentials")
            print("4. Deploy to Fly.io with JWT_SECRET")
            
        except Exception as e:
            print(f"\n❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
        
        break  # Exit after first db session

if __name__ == "__main__":
    asyncio.run(test_auth_system())
