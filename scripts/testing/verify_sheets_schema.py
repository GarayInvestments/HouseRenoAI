#!/usr/bin/env python3
"""
Verify Google Sheets Schema
Connects to Google Sheets API and verifies the actual schema matches expected schema
"""

import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuration
SHEET_ID = "1Wp1MZFTA2rCm55IMAkNmh6z_2-vEa0mdhEkcufQVnnI"
CREDENTIALS_FILE = "config/ultra-fresh-credentials.json"
EXPECTED_SCHEMA_FILE = "config/GC_Permit_Compliance_Schema.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def load_credentials():
    """Load Google Service Account credentials"""
    print(f"📁 Loading credentials from: {CREDENTIALS_FILE}")
    
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Error: Credentials file not found: {CREDENTIALS_FILE}")
        return None
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=SCOPES
        )
        print("✅ Credentials loaded successfully")
        return credentials
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None

def load_expected_schema():
    """Load the expected schema from JSON file"""
    print(f"\n📋 Loading expected schema from: {EXPECTED_SCHEMA_FILE}")
    
    if not os.path.exists(EXPECTED_SCHEMA_FILE):
        print(f"❌ Error: Schema file not found: {EXPECTED_SCHEMA_FILE}")
        return None
    
    try:
        with open(EXPECTED_SCHEMA_FILE, 'r') as f:
            schema = json.load(f)
        print(f"✅ Expected schema loaded: {len(schema['sheets'])} sheets defined")
        return schema
    except Exception as e:
        print(f"❌ Error loading schema: {e}")
        return None

def get_sheet_metadata(service, sheet_id):
    """Get all sheet metadata including names and column headers"""
    print(f"\n🔍 Fetching sheet metadata from Google Sheets...")
    print(f"   Sheet ID: {sheet_id}")
    
    try:
        # Get spreadsheet metadata
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=sheet_id,
            includeGridData=False
        ).execute()
        
        sheet_titles = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
        print(f"✅ Found {len(sheet_titles)} sheets in the spreadsheet")
        
        return spreadsheet, sheet_titles
    except HttpError as e:
        print(f"❌ HTTP Error: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Error fetching metadata: {e}")
        return None, None

def get_sheet_columns(service, sheet_id, sheet_name):
    """Get column headers from a specific sheet"""
    try:
        # Read the first row (headers) from the sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"'{sheet_name}'!1:1"
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
        
        return values[0]  # First row contains headers
    except Exception as e:
        print(f"   ⚠️  Error reading columns from '{sheet_name}': {e}")
        return []

def verify_schema(service, sheet_id, expected_schema):
    """Verify actual sheet structure matches expected schema"""
    print("\n" + "="*80)
    print("🔍 SCHEMA VERIFICATION")
    print("="*80)
    
    # Get actual sheets
    spreadsheet, actual_sheet_names = get_sheet_metadata(service, sheet_id)
    if not spreadsheet or not actual_sheet_names:
        return False
    
    expected_sheets = {sheet['name']: sheet for sheet in expected_schema['sheets']}
    
    print(f"\n📊 Comparison:")
    print(f"   Expected sheets: {len(expected_sheets)}")
    print(f"   Actual sheets:   {len(actual_sheet_names)}")
    
    all_match = True
    
    # Check each expected sheet
    for sheet_name, sheet_def in expected_sheets.items():
        print(f"\n{'─'*80}")
        print(f"📄 Sheet: {sheet_name}")
        print(f"{'─'*80}")
        
        if sheet_name not in actual_sheet_names:
            print(f"   ❌ MISSING: Sheet '{sheet_name}' not found in spreadsheet")
            all_match = False
            continue
        
        print(f"   ✅ Sheet exists")
        
        # Get actual columns
        actual_columns = get_sheet_columns(service, sheet_id, sheet_name)
        expected_columns = [col['name'] for col in sheet_def['columns']]
        
        print(f"   📋 Columns:")
        print(f"      Expected: {len(expected_columns)}")
        print(f"      Actual:   {len(actual_columns)}")
        
        # Compare columns
        missing_columns = set(expected_columns) - set(actual_columns)
        extra_columns = set(actual_columns) - set(expected_columns)
        
        if not missing_columns and not extra_columns:
            print(f"   ✅ All columns match perfectly")
        else:
            if missing_columns:
                print(f"   ⚠️  Missing columns: {sorted(missing_columns)}")
                all_match = False
            if extra_columns:
                print(f"   ℹ️  Extra columns: {sorted(extra_columns)}")
        
        # Show column details
        print(f"\n   Column Details:")
        for i, col_name in enumerate(expected_columns, 1):
            status = "✅" if col_name in actual_columns else "❌"
            col_def = next((c for c in sheet_def['columns'] if c['name'] == col_name), None)
            col_type = col_def['type'] if col_def else 'unknown'
            relation = f" → {col_def['relation']}" if col_def and 'relation' in col_def else ""
            print(f"      {status} {i:2d}. {col_name:<40} ({col_type}){relation}")
    
    # Check for unexpected sheets
    unexpected_sheets = set(actual_sheet_names) - set(expected_sheets.keys())
    if unexpected_sheets:
        print(f"\n{'─'*80}")
        print(f"ℹ️  Additional sheets found (not in schema):")
        for sheet_name in sorted(unexpected_sheets):
            print(f"   • {sheet_name}")
    
    return all_match

def main():
    """Main execution"""
    print("🏠 House Renovators AI - Google Sheets Schema Verification")
    print("="*80)
    
    # Load credentials
    credentials = load_credentials()
    if not credentials:
        return
    
    # Load expected schema
    expected_schema = load_expected_schema()
    if not expected_schema:
        return
    
    # Build Sheets service
    print("\n🔧 Building Google Sheets API service...")
    try:
        service = build('sheets', 'v4', credentials=credentials)
        print("✅ Service built successfully")
    except Exception as e:
        print(f"❌ Error building service: {e}")
        return
    
    # Verify schema
    match = verify_schema(service, SHEET_ID, expected_schema)
    
    # Final summary
    print("\n" + "="*80)
    if match:
        print("✅ VERIFICATION COMPLETE: Schema matches perfectly!")
    else:
        print("⚠️  VERIFICATION COMPLETE: Some differences found (see details above)")
    print("="*80)

if __name__ == "__main__":
    main()
