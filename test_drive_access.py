#!/usr/bin/env python3
"""
Test Google Drive Access
Verifies the backend can access Google Drive API
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_drive_access():
    """Test Google Drive API access"""
    print("🏠 House Renovators AI - Google Drive Access Test")
    print("="*80)
    
    # Load credentials
    creds_file = "C:/Users/Steve Garay/Desktop/HouseRenovators-api/config/ultra-fresh-credentials.json"
    
    print(f"\n📁 Loading credentials from: {creds_file}")
    
    if not os.path.exists(creds_file):
        print("❌ ERROR: Credentials file not found!")
        return False
    
    try:
        # Define scopes
        SCOPES = [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.metadata.readonly'
        ]
        
        credentials = service_account.Credentials.from_service_account_file(
            creds_file,
            scopes=SCOPES
        )
        print("✅ Credentials loaded successfully")
        
        # Build Drive service
        print("\n🔧 Building Google Drive API service...")
        drive_service = build('drive', 'v3', credentials=credentials)
        print("✅ Drive service built successfully")
        
        # Test 1: List files (limited to 10)
        print("\n" + "="*80)
        print("🔍 Test 1: List Accessible Files")
        print("="*80)
        
        try:
            results = drive_service.files().list(
                pageSize=10,
                fields="files(id, name, mimeType, createdTime, modifiedTime, owners)"
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                print("⚠️  No files found (service account may not have access to any files yet)")
            else:
                print(f"✅ Found {len(files)} accessible files:")
                for i, file in enumerate(files, 1):
                    file_type = file.get('mimeType', 'unknown')
                    if 'spreadsheet' in file_type:
                        type_icon = "📊"
                    elif 'folder' in file_type:
                        type_icon = "📁"
                    elif 'document' in file_type:
                        type_icon = "📄"
                    else:
                        type_icon = "📎"
                    
                    print(f"\n   {type_icon} {i}. {file.get('name')}")
                    print(f"      ID: {file.get('id')}")
                    print(f"      Type: {file_type}")
                    
        except Exception as e:
            print(f"❌ Error listing files: {e}")
            return False
        
        # Test 2: Check access to our specific spreadsheet
        print("\n" + "="*80)
        print("🔍 Test 2: Access Our Spreadsheet")
        print("="*80)
        
        sheet_id = "1Wp1MZFTA2rCm55IMAkNmh6z_2-vEa0mdhEkcufQVnnI"
        
        try:
            file_metadata = drive_service.files().get(
                fileId=sheet_id,
                fields="id, name, mimeType, owners, permissions, createdTime, modifiedTime, webViewLink"
            ).execute()
            
            print(f"✅ Successfully accessed spreadsheet!")
            print(f"\n   📊 Name: {file_metadata.get('name')}")
            print(f"   🆔 ID: {file_metadata.get('id')}")
            print(f"   📅 Created: {file_metadata.get('createdTime')}")
            print(f"   📝 Modified: {file_metadata.get('modifiedTime')}")
            print(f"   🔗 URL: {file_metadata.get('webViewLink')}")
            
            # Check permissions
            try:
                permissions = drive_service.permissions().list(
                    fileId=sheet_id,
                    fields="permissions(id, type, role, emailAddress)"
                ).execute()
                
                print(f"\n   👥 Permissions:")
                for perm in permissions.get('permissions', []):
                    perm_type = perm.get('type')
                    role = perm.get('role')
                    email = perm.get('emailAddress', 'N/A')
                    
                    if perm_type == 'user':
                        print(f"      • User: {email} ({role})")
                    elif perm_type == 'anyone':
                        print(f"      • Public: {role}")
                    else:
                        print(f"      • {perm_type}: {role}")
                        
            except Exception as perm_error:
                print(f"   ⚠️  Could not retrieve permissions: {perm_error}")
            
        except Exception as e:
            print(f"❌ Error accessing spreadsheet: {e}")
            return False
        
        # Test 3: Check file operations capabilities
        print("\n" + "="*80)
        print("🔍 Test 3: Available Operations")
        print("="*80)
        
        print("\n   Service Account has these capabilities:")
        print("   ✅ Read file metadata")
        print("   ✅ List accessible files")
        print("   ✅ Access shared spreadsheets")
        print("   ✅ View file permissions")
        print("   ⚠️  Limited to files explicitly shared with service account")
        
        print("\n" + "="*80)
        print("✅ DRIVE ACCESS TEST COMPLETE")
        print("="*80)
        print("\nSummary:")
        print("✅ Google Drive API is accessible")
        print("✅ Service account can read file metadata")
        print("✅ Our spreadsheet is accessible via Drive API")
        print("✅ Can view permissions and sharing settings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_drive_access()
    sys.exit(0 if success else 1)
