#!/usr/bin/env python3
"""
Simple script to fix private key newlines and create base64
"""
import json
import base64

# Load the credentials
with open('fresh-credentials.json', 'r') as f:
    creds = json.load(f)

# Get the private key and fix newlines
private_key = creds['private_key']
print(f"Original private key length: {len(private_key)}")
print(f"Contains \\n: {'\\n' in private_key}")

# Replace \\n with actual newlines
fixed_private_key = private_key.replace('\\n', '\n')
print(f"Fixed private key length: {len(fixed_private_key)}")
print(f"Fixed key ends correctly: {fixed_private_key.endswith('-----END PRIVATE KEY-----')}")

# Update the credentials
creds['private_key'] = fixed_private_key

# Create JSON string with proper formatting
json_string = json.dumps(creds, separators=(',', ':'))  # Compact JSON

# Encode to base64
base64_data = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')

print("\nBase64 encoded (fixed):")
print(base64_data)

# Test it
try:
    decoded = base64.b64decode(base64_data).decode('utf-8')
    test_creds = json.loads(decoded)
    print(f"\n✅ Validation:")
    print(f"   - Decodes successfully: True")
    print(f"   - Client email: {test_creds['client_email']}")
    print(f"   - Private key length: {len(test_creds['private_key'])}")
    print(f"   - Ends correctly: {test_creds['private_key'].endswith('-----END PRIVATE KEY-----')}")
    
    # Save the corrected version
    with open('corrected-credentials.json', 'w') as f:
        json.dump(test_creds, f, indent=2)
    print("   - Saved corrected credentials to corrected-credentials.json")
    
except Exception as e:
    print(f"❌ Validation failed: {e}")