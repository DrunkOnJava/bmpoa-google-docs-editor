#!/usr/bin/env python3
"""
Google Docs API Authentication Setup
This script helps you authenticate with Google Docs API
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents']

def authenticate():
    """Shows basic usage of the Docs API."""
    creds = None
    
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            # Check for credentials file
            if not os.path.exists('credentials.json'):
                print("\n" + "="*60)
                print("GOOGLE DOCS API SETUP REQUIRED")
                print("="*60)
                print("\nYou need to create OAuth2 credentials:")
                print("\n1. Go to: https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable the Google Docs API:")
                print("   - Go to APIs & Services > Library")
                print("   - Search for 'Google Docs API'")
                print("   - Click Enable")
                print("\n4. Create credentials:")
                print("   - Go to APIs & Services > Credentials")
                print("   - Click '+ CREATE CREDENTIALS' > OAuth client ID")
                print("   - Application type: Desktop app")
                print("   - Name: 'BMPOA Docs Editor' (or any name)")
                print("   - Download the credentials")
                print("\n5. Save the downloaded file as 'credentials.json' in:")
                print(f"   {os.getcwd()}")
                print("\n6. Run this script again")
                print("="*60)
                return None
            
            print("Starting OAuth2 flow...")
            print("A browser window will open for authentication.")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            print("✓ Credentials saved to token.json")
    
    return creds

def test_connection(creds):
    """Test the API connection"""
    try:
        service = build('docs', 'v1', credentials=creds)
        
        # Test with your document
        doc_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
        
        print(f"\nTesting connection with document {doc_id}...")
        document = service.documents().get(documentId=doc_id).execute()
        
        print("\n✓ SUCCESS! Connected to Google Docs API")
        print(f"Document Title: {document.get('title')}")
        print(f"Document ID: {doc_id}")
        
        # Show some stats
        body = document.get('body', {})
        content = body.get('content', [])
        print(f"Total elements: {len(content)}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error connecting to API: {e}")
        if "insufficient authentication scopes" in str(e):
            print("\nTip: Delete token.json and try again to re-authenticate with correct scopes")
        elif "The caller does not have permission" in str(e):
            print("\nTip: Make sure the document is shared with your Google account")
        return False

if __name__ == '__main__':
    print("Google Docs API Authentication Setup")
    print("="*40)
    
    # Authenticate
    creds = authenticate()
    
    if creds:
        print("\n✓ Authentication successful!")
        
        # Test the connection
        if test_connection(creds):
            print("\n" + "="*60)
            print("SETUP COMPLETE!")
            print("="*60)
            print("\nYou can now use the Google Docs API with your document.")
            print("The authentication token has been saved to 'token.json'")
            print("\nNext steps:")
            print("1. Run 'python work_with_doc.py' to use the full editor")
            print("2. Or create your own scripts using the saved credentials")
        else:
            print("\nAuthentication succeeded but couldn't access the document.")
            print("Check that the document is shared with your Google account.")
    else:
        print("\nSetup incomplete. Please follow the instructions above.")