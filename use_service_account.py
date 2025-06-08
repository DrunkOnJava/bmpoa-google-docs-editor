#!/usr/bin/env python3
"""
BMPOA Document Editor using Service Account
Uses the existing Google Docs Tool Service Account from HealthPortal project
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Document ID
DOCUMENT_ID = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"

# Service account email from your screenshot
SERVICE_ACCOUNT_EMAIL = "google-docs-tool@healthportal-445118.iam.gserviceaccount.com"

# Scopes
SCOPES = ['https://www.googleapis.com/auth/documents']

def authenticate_with_service_account():
    """Authenticate using service account key file"""
    # Check common locations for service account key
    possible_key_locations = [
        'service-account-key.json',
        os.path.expanduser('~/service-account-key.json'),
        os.path.expanduser('~/.config/gcloud/service-account-key.json'),
        'google-docs-tool-key.json',
        os.path.expanduser('~/google-docs-tool-key.json')
    ]
    
    key_file = None
    for location in possible_key_locations:
        if os.path.exists(location):
            key_file = location
            print(f"Found service account key at: {location}")
            break
    
    if not key_file:
        print("\nService account key file not found!")
        print("\nTo download the key:")
        print("1. Go to the service account page in Google Cloud Console")
        print("2. Click on 'google-docs-tool@healthportal-445118.iam.gserviceaccount.com'")
        print("3. Go to the 'Keys' tab")
        print("4. Click 'Add Key' > 'Create new key' > 'JSON'")
        print("5. Save the file as 'service-account-key.json' in this directory")
        return None
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            key_file,
            scopes=SCOPES
        )
        
        service = build('docs', 'v1', credentials=credentials)
        print("Successfully authenticated with service account!")
        return service
        
    except Exception as e:
        print(f"Error authenticating: {e}")
        return None

def share_document_with_service_account(document_id):
    """Instructions to share document with service account"""
    print(f"\nIMPORTANT: Make sure the document is shared with the service account!")
    print(f"\n1. Open the document: https://docs.google.com/document/d/{document_id}")
    print(f"2. Click 'Share' button")
    print(f"3. Add email: {SERVICE_ACCOUNT_EMAIL}")
    print(f"4. Give 'Editor' permissions")
    print(f"5. Click 'Send'\n")

def analyze_document(service, document_id):
    """Analyze the BMPOA document"""
    try:
        # Get document
        document = service.documents().get(documentId=document_id).execute()
        
        print(f"\n✅ Successfully accessed document!")
        print(f"Title: {document.get('title', 'Untitled')}")
        print(f"Document ID: {document_id}")
        
        # Extract content
        content = document.get('body', {}).get('content', [])
        
        # Count elements
        paragraphs = 0
        tables = 0
        total_text = ""
        
        for element in content:
            if 'paragraph' in element:
                paragraphs += 1
                paragraph = element['paragraph']
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        total_text += elem['textRun'].get('content', '')
            elif 'table' in element:
                tables += 1
        
        words = total_text.split()
        
        print(f"\nDocument Statistics:")
        print(f"- Total paragraphs: {paragraphs}")
        print(f"- Total tables: {tables}")
        print(f"- Total characters: {len(total_text)}")
        print(f"- Total words: {len(words)}")
        
        # Find key sections
        print(f"\nSearching for key sections...")
        sections = []
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                text = ""
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text += elem['textRun'].get('content', '')
                
                # Check if it's a header (all caps, short)
                if text.strip() and text.strip().isupper() and len(text.strip()) < 100:
                    sections.append(text.strip())
        
        print(f"\nFound {len(sections)} section headers:")
        for i, section in enumerate(sections[:15], 1):
            print(f"{i}. {section}")
        
        return document
        
    except HttpError as error:
        if error.resp.status == 403:
            print(f"\n❌ Access denied! The document needs to be shared with the service account.")
            share_document_with_service_account(document_id)
        else:
            print(f"\n❌ Error accessing document: {error}")
        return None

def perform_edits(service, document_id):
    """Perform batch edits on the document"""
    print("\n📝 Preparing document edits...")
    
    # Example: Add a timestamp at the beginning
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    requests = [
        # Add a note at the beginning
        {
            'insertText': {
                'location': {'index': 1},
                'text': f'[Last updated via API: {timestamp}]\n\n'
            }
        },
        # Make the timestamp italic
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': len(f'[Last updated via API: {timestamp}]') + 1
                },
                'textStyle': {
                    'italic': True,
                    'fontSize': {
                        'magnitude': 10,
                        'unit': 'PT'
                    }
                },
                'fields': 'italic,fontSize'
            }
        }
    ]
    
    try:
        result = service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()
        
        print("✅ Successfully updated document!")
        print(f"   - Added timestamp: {timestamp}")
        
        return True
        
    except HttpError as error:
        print(f"❌ Error updating document: {error}")
        return False

def main():
    print("=" * 60)
    print("BMPOA Document Editor - Service Account Version")
    print("=" * 60)
    
    # Authenticate
    service = authenticate_with_service_account()
    
    if not service:
        print("\n⚠️  Could not authenticate. Please set up the service account key.")
        return
    
    # Analyze document
    document = analyze_document(service, DOCUMENT_ID)
    
    if document:
        # Offer to make edits
        print("\n" + "=" * 60)
        response = input("\nWould you like to add a timestamp to the document? (y/n): ")
        
        if response.lower() == 'y':
            if perform_edits(service, DOCUMENT_ID):
                print("\n✨ Document successfully updated!")
                print(f"\nView the document: https://docs.google.com/document/d/{DOCUMENT_ID}")
        
        # Additional options
        print("\n" + "=" * 60)
        print("\nAdditional capabilities available:")
        print("1. Search and replace text")
        print("2. Apply formatting (bold, italic, colors)")
        print("3. Insert tables and lists")
        print("4. Add headers and footers")
        print("5. Create named ranges for easy navigation")
        print("\nThese features can be added to the script as needed.")

if __name__ == "__main__":
    main()