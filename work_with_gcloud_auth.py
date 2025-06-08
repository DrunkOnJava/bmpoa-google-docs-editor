#!/usr/bin/env python3
"""
Work with BMPOA Google Doc using gcloud authentication
"""

import json
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Document ID
doc_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"

# Use Application Default Credentials
print("Using Google Cloud application default credentials...")
credentials, project = google.auth.default(
    scopes=['https://www.googleapis.com/auth/documents']
)

# Build the service
service = build('docs', 'v1', credentials=credentials)

try:
    # Retrieve the document
    print(f"\nFetching document {doc_id}...")
    document = service.documents().get(documentId=doc_id).execute()
    
    print(f"\nDocument Title: {document.get('title')}")
    
    # Get content
    content = document.get('body', {}).get('content', [])
    print(f"Total elements: {len(content)}")
    
    # Extract text
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
    print("\nFirst 5 paragraphs:")
    for i, para in enumerate(text_content[:5]):
        print(f"\n{i+1}. {para[:100]}...")
        
    # Example: Search and replace
    print("\n\nWould you like to perform any edits? (y/n)")
    
except HttpError as error:
    print(f'An error occurred: {error}')