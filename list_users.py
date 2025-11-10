"""Quick script to list existing users."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.google_service import GoogleService
from app.config import settings

# Initialize Google service
google_service = GoogleService()
google_service.initialize()

# Read Users sheet
result = google_service.sheets_service.spreadsheets().values().get(
    spreadsheetId=settings.SHEET_ID,
    range="Users!A2:E100"
).execute()

values = result.get('values', [])

print("\n=== Existing Users ===\n")
if not values:
    print("No users found!")
else:
    for row in values:
        if len(row) >= 3:
            print(f"Email: {row[0]}")
            print(f"Name: {row[1]}")
            print(f"Role: {row[2] if len(row) > 2 else 'N/A'}")
            print("-" * 40)
