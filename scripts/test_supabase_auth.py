"""
Test script for Supabase Auth integration.

Usage:
1. Add Supabase keys to .env
2. Run: python scripts/test_supabase_auth.py
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Check environment variables
print("=" * 60)
print("SUPABASE AUTH CONFIGURATION CHECK")
print("=" * 60)

required_vars = [
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_JWT_SECRET"
]

missing = []
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Mask secrets
        if "KEY" in var or "SECRET" in var:
            display = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
        else:
            display = value
        print(f"✅ {var}: {display}")
    else:
        print(f"❌ {var}: NOT SET")
        missing.append(var)

print()

if missing:
    print("⚠️  MISSING CONFIGURATION:")
    print("   Please add these to your .env file:")
    for var in missing:
        print(f"   {var}=<value>")
    print()
    print("   See .env.supabase.template for instructions")
    exit(1)

print("✅ All Supabase environment variables configured!")
print()

# Test JWT verification
print("=" * 60)
print("TESTING JWT VERIFICATION")
print("=" * 60)

try:
    from app.services.supabase_auth_service import supabase_auth_service
    
    print(f"✅ Supabase service initialized")
    print(f"   URL: {supabase_auth_service.supabase_url}")
    print(f"   JWT Secret: {'Set' if supabase_auth_service.jwt_secret else 'Not set'}")
    print(f"   JWKS Client: {'Ready' if supabase_auth_service.jwks_client else 'Not configured'}")
    print()
    
    # Test with a sample JWT (will fail but tests the verification logic)
    print("Testing JWT verification logic...")
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    result = supabase_auth_service.verify_jwt(test_token)
    
    if result is None:
        print("✅ JWT verification working (test token correctly rejected)")
    else:
        print("⚠️  Unexpected: test token was accepted")
    
except Exception as e:
    print(f"❌ Error initializing service: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# Test database connection
print("=" * 60)
print("TESTING DATABASE CONNECTION")
print("=" * 60)

async def test_db():
    try:
        from app.db.session import AsyncSessionLocal
        from app.db.models import User
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as db:
            # Try to query users table
            result = await db.execute(select(User).limit(1))
            users = result.scalars().all()
            
            print(f"✅ Database connection successful")
            print(f"   Users in database: {len(users)}")
            
            if users:
                user = users[0]
                print(f"   Sample user: {user.email} (role: {user.role})")
            else:
                print(f"   No users yet - ready to create first user")
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

success = asyncio.run(test_db())
print()

if success:
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Create a test user in Supabase Dashboard:")
    print("   https://supabase.com/dashboard/project/dtfjzjhxtojkgfofrmrr/auth/users")
    print()
    print("2. Test login via frontend or API")
    print()
    print("3. Make first user an admin:")
    print("   psql 'postgresql://...' -c \"UPDATE users SET role='admin' WHERE email='your@email.com'\"")
else:
    print("❌ TESTS FAILED - Check errors above")
    exit(1)
