#!/usr/bin/env python3
"""
Test Supabase Auth signup to verify SMTP configuration
This will trigger a confirmation email if SMTP is configured
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

def test_signup_email():
    """Test signup to trigger confirmation email"""
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ Missing Supabase credentials")
        print("Set SUPABASE_URL and SUPABASE_ANON_KEY in .env")
        return False
    
    print("=== Testing Supabase Auth Email ===\n")
    print(f"Project: {SUPABASE_URL}")
    
    # Create Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    # Test email
    test_email = input("Enter email to test (will create user): ").strip()
    test_password = "TestPassword123!"
    
    print(f"\n📧 Testing signup for: {test_email}")
    print("This will send a confirmation email if SMTP is configured...")
    
    try:
        # Attempt signup
        response = supabase.auth.sign_up({
            "email": test_email,
            "password": test_password
        })
        
        if response.user:
            print(f"\n✅ User created: {response.user.id}")
            print(f"   Email: {response.user.email}")
            print(f"   Confirmed: {response.user.email_confirmed_at is not None}")
            
            if response.user.email_confirmed_at:
                print("\n⚠️ Email auto-confirmed (no confirmation email sent)")
                print("   This happens when email confirmation is disabled")
            else:
                print("\n📬 Confirmation email should be sent!")
                print(f"   Check {test_email} inbox")
                print("   If no email received:")
                print("   1. Check Supabase SMTP settings")
                print("   2. Verify 'Enable email confirmations' is ON")
                print("   3. Check spam folder")
            
            return True
        else:
            print("❌ No user created")
            return False
            
    except Exception as e:
        error_msg = str(e)
        
        if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
            print(f"\n⚠️ User already exists: {test_email}")
            print("Try a different email or delete the user in Supabase dashboard")
        else:
            print(f"\n❌ Error: {e}")
        
        return False

if __name__ == "__main__":
    test_signup_email()
