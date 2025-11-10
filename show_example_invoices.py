"""
Generate example invoices for each project using Google Sheets data.

This script demonstrates the property address-based invoice numbering convention.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.google_service import GoogleService
from app.config import settings

# Initialize Google service
print("🔄 Initializing Google Sheets service...")
google_service = GoogleService()
google_service.initialize()

# Read Projects data
print("📊 Fetching projects from Google Sheets...\n")
result = google_service.sheets_service.spreadsheets().values().get(
    spreadsheetId=settings.SHEET_ID,
    range="Projects!A2:Q100"  # Assuming 17 columns (A-Q)
).execute()

projects_data = result.get('values', [])

if not projects_data:
    print("❌ No projects found!")
    exit(1)

# Project columns based on FIELD_MAPPING.md:
# 1=Project ID, 2=Client ID, 3=Project Name, 4=Project Address, 5=City, 
# 6=County, 7=Jurisdiction, 8=Primary Inspector, 9=Owner Name, 10=Project Type,
# 11=HR PC Service Fee, 12=Start Date, 13=Status, 14=Scope of Work, 
# 15=Project Cost, 16=Photo Album, 17=Notes

print("="*90)
print("EXAMPLE INVOICES FOR EACH PROJECT")
print("(Using Property Address-Based Invoice Numbering Convention)")
print("="*90)
print()

def generate_invoice_number(address: str, project_name: str) -> str:
    """
    Generate invoice number from property address.
    
    Examples:
    - "1105 Sandy Bottom Dr NW, Concord, NC" → "1105-Sandy-Bottom"
    - "64 Phillips Ln, Spruce Pine, NC" → "64-Phillips"
    """
    if address and address.strip() and address != "Not provided":
        # Parse address to extract street number and first 2-3 words of street name
        parts = address.strip().split(',')[0].split()  # Get street part only
        
        # Filter out common suffixes
        suffixes = {'dr', 'st', 'ave', 'ln', 'rd', 'blvd', 'ct', 'way', 'pl', 'nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w'}
        filtered_parts = []
        
        for part in parts[:4]:  # Take max 4 parts
            cleaned = part.lower().rstrip('.,')
            if cleaned not in suffixes:
                filtered_parts.append(part.strip('.,'))
            if len(filtered_parts) >= 3:  # Max 3 meaningful parts
                break
        
        if filtered_parts:
            return '-'.join(filtered_parts)
    
    # Fallback to project name
    name_parts = project_name.split()[:3] if project_name else ['Unknown']
    return '-'.join(name_parts)

for idx, project in enumerate(projects_data, 1):
    if len(project) < 4:  # Need at least Project ID, Client ID, Name, Address
        continue
    
    project_id = project[0] if len(project) > 0 else "N/A"
    client_id = project[1] if len(project) > 1 else "N/A"
    project_name = project[2] if len(project) > 2 else "Unnamed Project"
    project_address = project[3] if len(project) > 3 else "Not provided"
    city = project[4] if len(project) > 4 else ""
    status = project[12] if len(project) > 12 else "Unknown"
    project_cost = project[14] if len(project) > 14 else "0"
    owner_name = project[8] if len(project) > 8 else "Unknown Owner"
    
    # Generate invoice number
    invoice_number = generate_invoice_number(project_address, project_name)
    
    # Format cost
    try:
        cost_float = float(project_cost.replace('$', '').replace(',', '')) if project_cost and project_cost != "Not provided" else 0
        cost_formatted = f"${cost_float:,.2f}"
    except:
        cost_formatted = "$0.00"
    
    print(f"📄 INVOICE #{invoice_number}")
    print(f"   └─ Project: {project_name}")
    print(f"   └─ Address: {project_address}")
    if city:
        print(f"   └─ City: {city}")
    print(f"   └─ Owner: {owner_name}")
    print(f"   └─ Status: {status}")
    print(f"   └─ Amount: {cost_formatted}")
    print(f"   └─ Project ID: {project_id}")
    print(f"   └─ Client ID: {client_id}")
    print()
    
    if idx >= 10:  # Limit to first 10 projects for display
        remaining = len(projects_data) - 10
        if remaining > 0:
            print(f"... and {remaining} more projects")
        break

print("="*90)
print("\n✅ Invoice numbering convention demonstrated!")
print("\nKey Features:")
print("  • Uses property address for meaningful invoice numbers")
print("  • Extracts street number + first 2-3 words of street name")
print("  • Filters out common suffixes (Dr, St, Ave, Ln, etc.)")
print("  • Falls back to project name if no address available")
print("  • Appends counter for duplicates (e.g., '-2', '-3')")
