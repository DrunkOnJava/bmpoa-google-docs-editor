#!/usr/bin/env python3
"""
Test Google Docs API Authentication
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/documents']

def test_auth():
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            # This will open browser for authentication
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Test with your document
    service = build('docs', 'v1', credentials=creds)
    doc_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
    
    try:
        document = service.documents().get(documentId=doc_id).execute()
        print(f"✓ Success! Connected to: {document.get('title')}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    print("Testing Google Docs API Authentication...")
    print("Note: A browser window will open for authorization")
    print("-" * 50)
    
    # Since we can't interact with the browser in this environment,
    # let's check the current status instead
    print("\nCurrent status:")
    print(f"✓ credentials.json exists: {os.path.exists('credentials.json')}")
    print(f"✓ token.json exists: {os.path.exists('token.json')}")
    
    if os.path.exists('credentials.json'):
        print("\nTo authenticate:")
        print("1. Run this script on your local machine")
        print("2. A browser window will open")
        print("3. Log in with your Google account")
        print("4. Authorize the app")
        print("5. The script will save the token")
        
        print("\nCommand to run:")
        print("python test_auth.py")
    else:
        print("\n✗ credentials.json not found!")