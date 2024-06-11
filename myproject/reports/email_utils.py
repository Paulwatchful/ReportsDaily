# reports/email_utils.py
import msal
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# OAuth2 configuration
CLIENT_ID = '4881cb76-76fb-42b5-a518-e5de054abf9c'
CLIENT_SECRET = 'f2f8Q~USc_UylE3sAVpJ9aVjm2wgE3AuqkAh2aV7'
TENANT_ID = '6450702d-c26c-4ab3-8d3d-acfe95670510'
AUTHORITY_URL = f'https://login.microsoftonline.com/{TENANT_ID}'
SCOPES = ["https://graph.microsoft.com/.default"]

def acquire_token():
    app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY_URL
    )
    result = app.acquire_token_for_client(scopes=SCOPES)
    if "access_token" in result:
        return result["access_token"]
    else:
        logger.error("Failed to acquire token: %s", result.get("error_description"))
        raise Exception("Failed to acquire token")

def fetch_shared_mailbox_emails(token, shared_mailbox_email):
    graph_url = f"https://graph.microsoft.com/v1.0/users/{shared_mailbox_email}/mailFolders/inbox/messages"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        '$top': 10  # Number of emails to fetch
    }
    response = requests.get(graph_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error("API call failed: %s", response.text)
        raise Exception("API call failed")
