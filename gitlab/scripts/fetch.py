import json
import os
import sys
import urllib.request
import urllib.parse

sci_tenant_url = os.environ.get("SCI_TENANT_URL", "")
sci_client_id = os.environ.get("SCI_CLIENT_ID", "")
sci_client_secret = os.environ.get("SCI_CLIENT_SECRET", "")

# --- Validate inputs ---
errors = []
if not sci_tenant_url:
    errors.append("SCI_TENANT_URL is required but not set")
if not sci_client_id:
    errors.append("SCI_CLIENT_ID is required but not set")
if not sci_client_secret:
    errors.append("SCI_CLIENT_SECRET is required but not set")
if errors:
    for e in errors:
        print(f"Error: {e}")
    sys.exit(1)

# --- Exchange client credentials for an SCI token ---
payload = urllib.parse.urlencode({
    "grant_type": "client_credentials",
    "client_id": sci_client_id,
    "client_secret": sci_client_secret,
    "resource": "urn:sap:identity:application:provider:name:build",
}).encode()

req = urllib.request.Request(
    f"{sci_tenant_url}/oauth2/token",
    data=payload,
    method="POST",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)
try:
    with urllib.request.urlopen(req) as resp:
        response = json.loads(resp.read())
except urllib.error.HTTPError as e:
    print(f"Error: SCI token request failed with status {e.code}: {e.read().decode()}")
    sys.exit(1)

sci_token = response.get("access_token")
if not sci_token:
    print(f"Error: sci_token was not retrieved. Response: {response}")
    sys.exit(1)

print("sci_token successfully retrieved")

# Write to dotenv artifact so downstream jobs can read SCI_TOKEN
with open("token.env", "w") as f:
    f.write(f"SCI_TOKEN={sci_token}\n")
