#!/usr/bin/env python3
"""
Simple Google Docs viewer and editor
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Document ID
doc_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"

# Check for service account key
service_account_file = os.path.expanduser('~/service-account-key.json')
if os.path.exists(service_account_file):
    print("Using service account credentials...")
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=['https://www.googleapis.com/auth/documents']
    )
else:
    print("Attempting to use OAuth2 flow...")
    from google_auth_oauthlib.flow import InstalledAppFlow
    
    # Check for credentials.json
    creds_file = 'credentials.json'
    if not os.path.exists(creds_file):
        print(f"\nError: {creds_file} not found!")
        print("Please download OAuth2 credentials from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Create OAuth 2.0 Client ID (Desktop app)")
        print("3. Download and save as credentials.json")
        exit(1)
    
    flow = InstalledAppFlow.from_client_secrets_file(
        creds_file, 
        ['https://www.googleapis.com/auth/documents']
    )
    credentials = flow.run_local_server(port=0)
    
    # Save the credentials for next run
    with open('token.json', 'w') as token:
        token.write(credentials.to_json())

# Build the service
service = build('docs', 'v1', credentials=credentials)

try:
    # Get document
    print(f"\nFetching document...")
    document = service.documents().get(documentId=doc_id).execute()
    
    print(f"\nDocument Title: {document.get('title')}")
    
    # Extract and display content
    content = document.get('body', {}).get('content', [])
    
    text_content = []
    for element in content:
        if 'paragraph' in element:
            paragraph = element['paragraph']
            text = ''
            for elem in paragraph.get('elements', []):
                if 'textRun' in elem:
                    text += elem['textRun'].get('content', '')
            if text.strip():
                text_content.append(text.strip())
    
    print(f"\nTotal paragraphs: {len(text_content)}")
    print("\nFirst 10 paragraphs:")
    for i, para in enumerate(text_content[:10]):
        print(f"\n{i+1}. {para[:150]}...")
        
    # Save to file for analysis
    with open('document_content.txt', 'w') as f:
        f.write('\n\n'.join(text_content))
    print(f"\nFull document saved to document_content.txt")
    
    # Document structure
    print(f"\nDocument structure elements: {len(content)}")
    
except HttpError as error:
    print(f'An error occurred: {error}')
    if 'insufficient authentication scopes' in str(error):
        print("\nTry deleting token.json and running again to re-authenticate.")