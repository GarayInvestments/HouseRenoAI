"""
Setup Payments Sheet in Google Sheets

This script:
1. Creates the Payments tab (if it doesn't exist)
2. Adds header row with 11 columns
3. Sets up data validation for Payment Method and Status columns
"""

import asyncio
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
Setup Payments Sheet in Google Sheets

Run this script while the backend is running (it uses the initialized Google service).
Alternatively, start the backend first, then run this script.
"""

import asyncio
import sys
import requests

API_BASE = "http://localhost:8000"


async def setup_payments_sheet():
    """Create and configure Payments sheet via API"""
    
    print("🚀 Setting up Payments sheet...")
    
    # Note: This requires creating an admin endpoint or using direct Google Sheets API
    # For now, let's create a simpler approach using direct gspread
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        credentials_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        spreadsheet_id = os.getenv('SHEET_ID')
        
        if not credentials_file or not spreadsheet_id:
            print("❌ Missing GOOGLE_SERVICE_ACCOUNT_FILE or SHEET_ID in .env")
            return False
        
        print(f"🔧 Using credentials file: {credentials_file}")
        print(f"🔧 Spreadsheet ID: {spreadsheet_id}")
        
        # Initialize credentials
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=SCOPES
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        
        print("✅ Google Sheets API initialized!")
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    print("🚀 Setting up Payments sheet...")
    
    # Step 1: Create Payments tab
    print("\n📋 Step 1: Creating Payments tab...")
    try:
        # Check if sheet already exists
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
        
        if 'Payments' in sheet_names:
            print("✅ Payments sheet already exists!")
        else:
            # Create new sheet
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': 'Payments',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 11
                            }
                        }
                    }
                }]
            }
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()
            print("✅ Payments tab created successfully!")
            
    except Exception as e:
        print(f"❌ Failed to create Payments tab: {e}")
        return False
    
    # Step 2: Add header row
    print("\n📋 Step 2: Adding header row...")
    headers = [
        'Payment ID',
        'Invoice ID',
        'Project ID',
        'Client ID',
        'Amount',
        'Payment Date',
        'Payment Method',
        'Status',
        'QB Payment ID',
        'Transaction ID',
        'Notes'
    ]
    
    try:
        # Update first row with headers
        request_body = {
            'values': [headers]
        }
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Payments!A1:K1',
            valueInputOption='RAW',
            body=request_body
        ).execute()
        
        print("✅ Header row added successfully!")
        print(f"   Columns: {', '.join(headers)}")
    except Exception as e:
        print(f"❌ Failed to add headers: {e}")
        return False
    
    # Step 3: Set up data validation
    print("\n📋 Step 3: Setting up data validation...")
    
    try:
        # Get sheet ID for Payments tab
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        payments_sheet_id = None
        for sheet in spreadsheet['sheets']:
            if sheet['properties']['title'] == 'Payments':
                payments_sheet_id = sheet['properties']['sheetId']
                break
        
        if not payments_sheet_id:
            print("❌ Could not find Payments sheet ID")
            return False
        
        # Prepare data validation requests
        requests = []
        
        # Payment Method validation (Column G = index 6)
        payment_methods = ['Zelle', 'Check', 'Cash', 'Credit Card', 'ACH', 'Other']
        requests.append({
            'setDataValidation': {
                'range': {
                    'sheetId': payments_sheet_id,
                    'startRowIndex': 1,  # Start from row 2 (skip header)
                    'endRowIndex': 1000,
                    'startColumnIndex': 6,  # Column G
                    'endColumnIndex': 7
                },
                'rule': {
                    'condition': {
                        'type': 'ONE_OF_LIST',
                        'values': [{'userEnteredValue': method} for method in payment_methods]
                    },
                    'showCustomUi': True,
                    'strict': True
                }
            }
        })
        
        # Status validation (Column H = index 7)
        statuses = ['Pending', 'Completed', 'Failed', 'Refunded']
        requests.append({
            'setDataValidation': {
                'range': {
                    'sheetId': payments_sheet_id,
                    'startRowIndex': 1,  # Start from row 2 (skip header)
                    'endRowIndex': 1000,
                    'startColumnIndex': 7,  # Column H
                    'endColumnIndex': 8
                },
                'rule': {
                    'condition': {
                        'type': 'ONE_OF_LIST',
                        'values': [{'userEnteredValue': status} for status in statuses]
                    },
                    'showCustomUi': True,
                    'strict': True
                }
            }
        })
        
        # Execute batch update
        body = {'requests': requests}
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
        
        print("✅ Data validation set up successfully!")
        print(f"   Payment Method: {', '.join(payment_methods)}")
        print(f"   Status: {', '.join(statuses)}")
        
    except Exception as e:
        print(f"⚠️  Could not set up data validation: {e}")
        print("   (This is optional - sheet is still functional)")
    
    print("\n✅ Payments sheet setup complete!")
    print("\n📊 Sheet Structure:")
    print("   - 11 columns: Payment ID → Notes")
    print("   - Data validation on Payment Method and Status")
    print("   - Ready for payment tracking and QB sync")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Payments Sheet Setup Script")
    print("=" * 60)
    
    success = asyncio.run(setup_payments_sheet())
    
    if success:
        print("\n🎉 Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)
