"""
Quick script to verify sheet structures by querying production API
"""
import requests
import json

API_URL = "https://houserenoai.onrender.com"

# You'll need to login first to get a token
print("=" * 80)
print("SHEET STRUCTURE VERIFICATION VIA PRODUCTION API")
print("=" * 80)
print()
print("To verify sheet structures, we need to query the production API.")
print("This requires authentication.")
print()
print("Manual steps:")
print("1. Login to get token:")
print(f"   curl -X POST {API_URL}/v1/auth/login -H 'Content-Type: application/json' \\")
print("        -d '{\"email\":\"your@email.com\",\"password\":\"your_password\"}'")
print()
print("2. Then query each endpoint:")
print(f"   curl {API_URL}/v1/clients -H 'Authorization: Bearer <token>'")
print(f"   curl {API_URL}/v1/projects -H 'Authorization: Bearer <token>'")
print()
print("This will show you the ACTUAL column names from Google Sheets.")
print()
print("=" * 80)
