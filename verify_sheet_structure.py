#!/usr/bin/env python3
"""Verify actual Google Sheets structure from API"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up environment before importing
from dotenv import load_dotenv
load_dotenv()

from app.services import google_service as google_service_module

async def main():
    # Use the existing google_service singleton
    google_service = google_service_module.google_service
    
    if not google_service:
        print("ERROR: Google service not initialized. Make sure .env file exists with SHEET_ID and credentials.")
        return
    
    # List of sheets to check
    sheets = [
        "Clients",
        "Projects", 
        "Permits",
        "Users",
        "Sessions",
        "QB_Tokens",
        "Documents"
    ]
    
    print("=" * 80)
    print("VERIFYING ACTUAL GOOGLE SHEETS STRUCTURE FROM API")
    print("=" * 80)
    
    for sheet_name in sheets:
        try:
            print(f"\n{'=' * 80}")
            print(f"📋 {sheet_name.upper()} SHEET")
            print(f"{'=' * 80}")
            
            # Read first 3 rows (headers + 2 samples)
            data = await google_service.read_sheet_data(f'{sheet_name}!A1:ZZ3')
            
            if data and len(data) > 0:
                headers = data[0]
                # Filter out empty columns
                actual_headers = [h for h in headers if h and h.strip()]
                
                print(f"\n✅ Found {len(actual_headers)} columns:\n")
                
                for i, header in enumerate(actual_headers, 1):
                    print(f"  {i:2d}. {header}")
                
                if len(data) > 1 and any(data[1]):
                    print(f"\n📄 Sample data (first row):")
                    print("-" * 80)
                    for header, value in zip(actual_headers, data[1][:len(actual_headers)]):
                        if value:  # Only show non-empty values
                            display_value = str(value)[:80] if len(str(value)) > 80 else value
                            print(f"  {header}: {display_value}")
                else:
                    print(f"\n⚠️  No sample data available (empty sheet)")
            else:
                print(f"❌ No data found or sheet doesn't exist")
                
        except Exception as e:
            print(f"❌ Error reading {sheet_name}: {e}")
    
    print(f"\n{'=' * 80}")
    print("VERIFICATION COMPLETE")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    asyncio.run(main())
