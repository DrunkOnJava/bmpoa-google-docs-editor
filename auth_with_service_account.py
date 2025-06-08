#!/usr/bin/env python3
"""
Authenticate with Google Docs API using Service Account
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Service account email from your screenshot
SERVICE_ACCOUNT_EMAIL = "google-docs-tool@healthportal-445118.iam.gserviceaccount.com"

def authenticate_with_service_account(key_file_path):
    """Authenticate using service account credentials"""
    
    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/documents']
    
    try:
        # Create credentials from service account key file
        credentials = service_account.Credentials.from_service_account_file(
            key_file_path,
            scopes=SCOPES
        )
        
        # Build the service
        service = build('docs', 'v1', credentials=credentials)
        
        print(f"✓ Authenticated with service account: {SERVICE_ACCOUNT_EMAIL}")
        return service
        
    except Exception as e:
        print(f"✗ Error authenticating: {e}")
        return None

def test_document_access(service, doc_id):
    """Test access to a Google Doc"""
    try:
        document = service.documents().get(documentId=doc_id).execute()
        
        print(f"\n✅ SUCCESS! Can access document")
        print(f"Title: {document.get('title')}")
        print(f"Document ID: {doc_id}")
        
        # Get some stats
        content = document.get('body', {}).get('content', [])
        print(f"Total elements: {len(content)}")
        
        # Count paragraphs
        paragraphs = [elem for elem in content if 'paragraph' in elem]
        print(f"Total paragraphs: {len(paragraphs)}")
        
        return True
        
    except HttpError as e:
        print(f"\n❌ Error accessing document: {e}")
        
        if "not have permission" in str(e):
            print(f"\n⚠️  The document needs to be shared with the service account:")
            print(f"   Email: {SERVICE_ACCOUNT_EMAIL}")
            print(f"\nSteps to share:")
            print(f"1. Open https://docs.google.com/document/d/{doc_id}")
            print(f"2. Click 'Share' button")
            print(f"3. Add email: {SERVICE_ACCOUNT_EMAIL}")
            print(f"4. Give 'Editor' or 'Viewer' permission")
            print(f"5. Click 'Send'")
            
        return False

def main():
    print("Google Docs API - Service Account Authentication")
    print("="*50)
    
    # Check for service account key file
    key_files = [
        "service-account-key.json",
        "google-docs-tool-key.json",
        os.path.expanduser("~/Downloads/healthportal-445118-*.json")
    ]
    
    key_file = None
    for file in key_files:
        if os.path.exists(file):
            key_file = file
            break
    
    if not key_file:
        # Check Downloads folder for any service account key
        import glob
        downloads = glob.glob(os.path.expanduser("~/Downloads/*healthportal*.json"))
        if downloads:
            key_file = downloads[0]
    
    if not key_file:
        print("\n❌ No service account key file found!")
        print("\nTo download the key:")
        print("1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts")
        print("2. Click on: google-docs-tool@healthportal-445118.iam.gserviceaccount.com")
        print("3. Go to 'Keys' tab")
        print("4. Click 'Add Key' > 'Create new key'")
        print("5. Choose 'JSON' format")
        print("6. Save the file in this directory as 'service-account-key.json'")
        return
    
    print(f"\n✓ Found service account key: {key_file}")
    
    # Authenticate
    service = authenticate_with_service_account(key_file)
    
    if service:
        # Test with the BMPOA document
        doc_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
        print(f"\nTesting access to BMPOA document...")
        
        if test_document_access(service, doc_id):
            print("\n✅ Everything is working! You can now use the Google Docs API.")
            
            # Save a simple config for future use
            config = {
                "service_account_email": SERVICE_ACCOUNT_EMAIL,
                "key_file": key_file,
                "document_id": doc_id
            }
            
            with open("google_docs_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            print("\n✓ Configuration saved to google_docs_config.json")

if __name__ == "__main__":
    main()