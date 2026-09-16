import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error

sci_tenant_url = os.environ.get("SCI_TENANT_URL", "")
sci_client_id = os.environ.get("SCI_CLIENT_ID", "")
github_output = os.environ["GITHUB_OUTPUT"]

# --- Validate inputs ---
errors = []
if not sci_tenant_url:
    errors.append("input 'SCI_TENANT_URL' is required but not set")
if not sci_client_id:
    errors.append("input 'SCI_CLIENT_ID' is required but not set")
if errors:
    for e in errors:
        print(f"Error: {e}")
    sys.exit(1)

# --- Get short-lived GitHub-issued JWT ---
token_request_url = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]
token_request_token = os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]

req = urllib.request.Request(
    f"{token_request_url}&audience={sci_tenant_url}",
    headers={
        "Authorization": f"Bearer {token_request_token}",
        "Accept": "application/json; api-version=2.0",
        "Content-Type": "application/json",
    },
)
try:
    with urllib.request.urlopen(req) as resp:
        github_jwt = json.loads(resp.read()).get("value")
except urllib.error.HTTPError as e:
    print(f"Error: GitHub OIDC token request failed with status {e.code}")
    sys.exit(1)
except urllib.error.URLError:
    print("Error: GitHub OIDC token request could not reach the token endpoint")
    sys.exit(1)

if not github_jwt:
    print("Error: GitHub response does not contain an OIDC token")
    sys.exit(1)

print(f"::add-mask::{github_jwt}")

# --- Exchange GitHub JWT for SCI token ---
payload = urllib.parse.urlencode({
    "grant_type": "client_credentials",
    "client_id": sci_client_id,
    "resource": "urn:sap:identity:application:provider:name:build",
    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    "client_assertion": github_jwt,
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
    print(f"Error: SCI token request failed with status {e.code}")
    sys.exit(1)
except urllib.error.URLError:
    print("Error: SCI token request could not reach the token endpoint")
    sys.exit(1)

sci_token = response.get("access_token")
if not sci_token:
    print("Error: SCI response does not contain access_token")
    sys.exit(1)

print("sci_token successfully retrieved")

# Mask the token in logs and write output
print(f"::add-mask::{sci_token}")
with open(github_output, "a") as f:
    f.write(f"sciToken={sci_token}\n")
