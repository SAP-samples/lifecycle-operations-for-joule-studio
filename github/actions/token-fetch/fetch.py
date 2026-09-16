import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error

sci_tenant_url = os.environ.get("SCI_TENANT_URL", "")
sci_client_id = os.environ.get("SCI_CLIENT_ID", "")
sci_client_secret = os.environ.get("SCI_CLIENT_SECRET", "")
github_output = os.environ["GITHUB_OUTPUT"]

# --- Validate inputs ---
errors = []
if not sci_tenant_url:
    errors.append("input 'SCI_TENANT_URL' is required but not set")
if not sci_client_id:
    errors.append("input 'SCI_CLIENT_ID' is required but not set")
if not sci_client_secret:
    errors.append("input 'SCI_CLIENT_SECRET' is required but not set")
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

endpoint = sci_tenant_url.rstrip("/") + "/oauth2/token"

req = urllib.request.Request(
    endpoint,
    data=payload,
    method="POST",
    headers={
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    },
)
try:
    with urllib.request.urlopen(req) as resp:
        response = json.loads(resp.read())
except urllib.error.HTTPError as e:
    print(f"Error: SCI token request failed with status {e.code}")
    sys.exit(1)
except urllib.error.URLError:
    print("Error: SCI token request could not reach the token endpoint")
    sys.exit(1)

sci_token = response.get("access_token")
if not sci_token:
    print("Error: SCI response does not contain access_token")
    sys.exit(1)

print("SCI token successfully retrieved")

# Mask the token in logs and write output
print(f"::add-mask::{sci_token}")
with open(github_output, "a") as f:
    f.write(f"sciToken={sci_token}\n")
