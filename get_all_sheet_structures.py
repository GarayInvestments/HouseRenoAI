#!/usr/bin/env python3
"""Get structure of all tabs in Google Sheets"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services import google_service as google_service_module

async def main():
    google_service = google_service_module.google_service
    
    if not google_service:
        print("ERROR: Google service not initialized")
        return
    
    # List of known tabs/sheets
    tabs = [
        "Clients",
        "Projects", 
        "Permits",
        "Users",
        "Sessions",
        "QB_Tokens",
        "Documents"
    ]
    
    print("=" * 80)
    print("GOOGLE SHEETS STRUCTURE - ALL TABS")
    print("=" * 80)
    
    for tab_name in tabs:
        try:
            print(f"\n{'=' * 80}")
            print(f"📋 {tab_name.upper()} SHEET")
            print(f"{'=' * 80}")
            
            # Read first 2 rows (headers + one sample)
            data = await google_service.read_sheet_data(f'{tab_name}!A1:ZZ2')
            
            if data and len(data) > 0:
                headers = data[0]
                print(f"\n✅ Found {len(headers)} columns:\n")
                
                for i, header in enumerate(headers, 1):
                    if header:  # Skip empty columns
                        print(f"  {i:2d}. {header}")
                
                if len(data) > 1:
                    sample_row = data[1]
                    print(f"\n📄 Sample data (first row):")
                    print("-" * 80)
                    for i, (header, value) in enumerate(zip(headers, sample_row)):
                        if header:
                            display_value = value[:50] if len(str(value)) > 50 else value
                            print(f"  {header}: {display_value}")
            else:
                print(f"❌ No data found or sheet doesn't exist")
                
        except Exception as e:
            print(f"❌ Error reading {tab_name}: {e}")
    
    print(f"\n{'=' * 80}")
    print("END OF SHEET STRUCTURES")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    asyncio.run(main())
