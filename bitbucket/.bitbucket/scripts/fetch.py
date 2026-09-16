import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error

# --- Read configuration from environment (Bitbucket repository variables) ---
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

# --- Exchange client credentials for an SCI access token ---
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
    # Only surface status and OAuth error fields, never the raw body which
    # may contain sensitive information.
    detail = ""
    try:
        body = json.loads(e.read())
        detail = f": {body.get('error')} - {body.get('error_description')}"
    except Exception:
        pass
    print(f"Error: SCI token request failed with status {e.code}{detail}")
    sys.exit(1)
except urllib.error.URLError as e:
    print(f"Error: SCI token request failed: {e.reason}")
    sys.exit(1)

sci_token = response.get("access_token")
if not sci_token:
    print("Error: SCI response does not contain access_token")
    sys.exit(1)

# Write to a dotenv file so the pipeline can read SCI_TOKEN. Do not print
# the token itself. The pipeline sets umask 077, so the file is created 0600.
with open("token.env", "w") as f:
    f.write(f"SCI_TOKEN={sci_token}\n")

print("SCI access token received successfully.")
