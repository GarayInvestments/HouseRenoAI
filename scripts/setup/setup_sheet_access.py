#!/usr/bin/env python3
"""
Grant Service Account Access to Google Sheets
Checks current permissions and provides instructions to grant access
"""

import json
import os
from pathlib import Path

def check_service_account():
    """Check service account configuration"""
    print("🏠 House Renovators AI - Service Account Access Setup")
    print("="*80)
    
    # Load credentials
    creds_path = Path("../config/ultra-fresh-credentials.json")
    if not creds_path.exists():
        creds_path = Path("config/ultra-fresh-credentials.json")
    
    if not creds_path.exists():
        print("❌ ERROR: Credentials file not found!")
        return
    
    print(f"\n📁 Loading credentials from: {creds_path}")
    
    with open(creds_path, 'r') as f:
        creds = json.load(f)
    
    service_account_email = creds.get('client_email', '')
    project_id = creds.get('project_id', '')
    
    print(f"\n✅ Service Account Information:")
    print(f"   Email: {service_account_email}")
    print(f"   Project ID: {project_id}")
    
    # Sheet information
    sheet_id = "1Wp1MZFTA2rCm55IMAkNmh6z_2-vEa0mdhEkcufQVnnI"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
    
    print(f"\n📊 Google Sheet:")
    print(f"   Sheet ID: {sheet_id}")
    print(f"   URL: {sheet_url}")
    
    # Instructions
    print("\n" + "="*80)
    print("📝 ACCESS SETUP INSTRUCTIONS")
    print("="*80)
    
    print("""
To grant the service account access to your Google Sheet:

1. Open the Google Sheet in your browser:
   👉 https://docs.google.com/spreadsheets/d/1Wp1MZFTA2rCm55IMAkNmh6z_2-vEa0mdhEkcufQVnnI

2. Click the "Share" button (top-right corner)

3. In the "Add people and groups" field, paste this email:
   📧 house-renovators-service@house-renovators-ai.iam.gserviceaccount.com

4. Set the permission level:
   ✅ Recommended: "Editor" (allows read and write)
   ⚠️  Minimum: "Viewer" (read-only, limited functionality)

5. IMPORTANT: Uncheck "Notify people" (service accounts don't receive emails)

6. Click "Share" or "Done"

7. Verify access by running:
   python backend/test_google_access.py
""")
    
    print("="*80)
    print("📋 QUICK REFERENCE")
    print("="*80)
    print(f"""
Service Account Email (copy this):
{service_account_email}

Google Sheet URL (open this):
{sheet_url}

Test Command (run this after granting access):
python backend/test_google_access.py
""")
    
    print("="*80)
    print("\n💡 TIP: After granting access, it may take a few seconds to propagate.")
    print("    If the test fails, wait 30 seconds and try again.\n")

if __name__ == "__main__":
    check_service_account()
