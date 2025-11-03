import json
import base64

# Read the credentials file
with open('perfect-credentials.json', 'r') as f:
    credentials = json.load(f)

# Ensure the private key ends correctly
private_key = credentials['private_key']
if not private_key.endswith('\n'):
    private_key += '\n'
    credentials['private_key'] = private_key

print(f"Private key length: {len(private_key)}")
print(f"Private key ends correctly: {private_key.endswith('-----END PRIVATE KEY-----\\n')}")

# Convert to JSON string and encode to base64
credentials_json = json.dumps(credentials)
base64_encoded = base64.b64encode(credentials_json.encode('utf-8')).decode('utf-8')

# Save the payload for Render API
payload = {
    "key": "GOOGLE_SERVICE_ACCOUNT_BASE64",
    "value": base64_encoded
}

with open('perfect-base64-payload.json', 'w') as f:
    json.dump(payload, f, indent=2)

print(f"Base64 encoded length: {len(base64_encoded)}")
print("Payload saved to perfect-base64-payload.json")

# Test decode to verify
decoded_test = base64.b64decode(base64_encoded).decode('utf-8')
test_credentials = json.loads(decoded_test)
print(f"Test decode private key ends correctly: {test_credentials['private_key'].endswith('-----END PRIVATE KEY-----\\n')}")