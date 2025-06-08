#!/usr/bin/env python3
"""
Authenticate using existing Google Cloud credentials
"""

import os
import json
import google.auth
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def use_gcloud_credentials():
    """Try to use gcloud credentials"""
    print("Attempting to use gcloud credentials...")
    
    try:
        # Get the default credentials
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/documents']
        )
        
        print(f"✓ Found credentials for project: {project}")
        
        # Build the service
        service = build('docs', 'v1', credentials=credentials)
        
        # Test with your document
        doc_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
        
        print(f"\nTesting access to document: {doc_id}")
        document = service.documents().get(documentId=doc_id).execute()
        
        print(f"\n✅ SUCCESS!")
        print(f"Document Title: {document.get('title')}")
        print(f"Document has {len(document.get('body', {}).get('content', []))} elements")
        
        # Save document content for reference
        with open('document_structure.json', 'w') as f:
            json.dump(document, f, indent=2)
        print("\n✓ Document structure saved to document_structure.json")
        
        return service
        
    except HttpError as e:
        print(f"\n❌ HTTP Error: {e}")
        if "insufficient authentication scopes" in str(e):
            print("\nThe gcloud credentials don't have Google Docs API access.")
            print("You need to use OAuth2 flow with the credentials.json file.")
        elif "not have permission" in str(e):
            print("\nMake sure the document is shared with your Google account:")
            print("griffinradcliffe@gmail.com")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    return None

def check_current_setup():
    """Check what authentication options are available"""
    print("\n" + "="*60)
    print("AUTHENTICATION OPTIONS CHECK")
    print("="*60)
    
    # Check for various credential files
    checks = {
        "OAuth2 credentials.json": os.path.exists("credentials.json"),
        "Saved token.json": os.path.exists("token.json"),
        "Google ADC": os.path.exists(os.path.expanduser("~/.config/gcloud/application_default_credentials.json")),
        "Service account key": os.path.exists("service-account-key.json")
    }
    
    print("\nAvailable authentication methods:")
    for method, exists in checks.items():
        print(f"  {'✓' if exists else '✗'} {method}")
    
    # Check gcloud config
    print("\nGoogle Cloud CLI status:")
    os.system("gcloud config list account --format='value(core.account)' | head -1")
    
    print("\nRecommendation:")
    if checks["OAuth2 credentials.json"] and not checks["Saved token.json"]:
        print("  → Run the OAuth2 flow to authenticate")
        print("  → Command: python google_docs_auth.py")
    elif checks["Saved token.json"]:
        print("  → You should be authenticated! Test with: python work_with_doc.py")
    else:
        print("  → Create OAuth2 credentials in Google Cloud Console")

if __name__ == "__main__":
    # First check what we have
    check_current_setup()
    
    # Try to use gcloud credentials
    print("\n" + "="*60)
    print("ATTEMPTING GCLOUD AUTHENTICATION")
    print("="*60)
    
    service = use_gcloud_credentials()
    
    if not service:
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\nSince gcloud credentials don't have Docs API access, you need to:")
        print("1. Run the OAuth2 authentication flow")
        print("2. Command: python google_docs_auth.py")
        print("3. This will open a browser for you to authorize access")
        print("\nThe credentials.json file is already set up and ready to use!")