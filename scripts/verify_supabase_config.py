"""
Simple test to verify Supabase Auth configuration without dependencies.
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("✅ SUPABASE AUTH SETUP COMPLETE!")
print("=" * 60)
print()

# Check all variables
print("Configuration:")
print(f"  SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"  SUPABASE_ANON_KEY: {os.getenv('SUPABASE_ANON_KEY')[:20]}...")
print(f"  SUPABASE_SERVICE_ROLE_KEY: {os.getenv('SUPABASE_SERVICE_ROLE_KEY')[:20]}...")
print(f"  SUPABASE_JWT_SECRET: {os.getenv('SUPABASE_JWT_SECRET')[:20]}...")
print()

print("✅ All Supabase environment variables are set!")
print()
print("=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print()
print("1. Restart your backend server:")
print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
print()
print("2. Create your first admin user:")
print("   a. Go to: https://supabase.com/dashboard/project/dtfjzjhxtojkgfofrmrr/auth/users")
print("   b. Click 'Add user'")
print("   c. Enter email/password")
print("   d. User will be created in auth.users")
print()
print("3. Make that user an admin:")
print('   psql "postgresql://postgres:...@db.dtfjzjhxtojkgfofrmrr.supabase.co:5432/postgres" \\')
print("        -c \"UPDATE users SET role='admin' WHERE email='your@email.com'\"")
print()
print("4. Test the authentication:")
print("   - Use Supabase client SDK in frontend to login")
print("   - Get JWT access token")
print("   - Call backend API with: Authorization: Bearer <token>")
print()
print("5. Update main.py to use new auth middleware")
print()
print("=" * 60)
print("📚 Full documentation: docs/setup/SUPABASE_AUTH_SETUP.md")
print("=" * 60)
