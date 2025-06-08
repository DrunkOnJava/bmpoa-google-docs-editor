#!/usr/bin/env python3
"""
View Google Doc using Application Default Credentials
"""

import os
import json
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Document ID
doc_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"

print("Setting up authentication...")

# Use ADC with correct scopes
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.expanduser('~/.config/gcloud/application_default_credentials.json')

# Get credentials with required scopes
credentials, project = google.auth.default(
    scopes=['https://www.googleapis.com/auth/documents.readonly']
)

# Build service
service = build('docs', 'v1', credentials=credentials)

try:
    # Get document
    print(f"\nFetching document {doc_id}...")
    document = service.documents().get(documentId=doc_id).execute()
    
    title = document.get('title', 'Untitled')
    print(f"\nDocument Title: {title}")
    
    # Extract content
    content = document.get('body', {}).get('content', [])
    
    # Extract text
    all_text = []
    for element in content:
        if 'paragraph' in element:
            paragraph = element['paragraph']
            para_text = ''
            for elem in paragraph.get('elements', []):
                if 'textRun' in elem:
                    para_text += elem['textRun'].get('content', '')
            if para_text.strip():
                all_text.append(para_text.strip())
    
    print(f"\nDocument Statistics:")
    print(f"- Total paragraphs: {len(all_text)}")
    print(f"- Total characters: {sum(len(p) for p in all_text)}")
    print(f"- Total words: {sum(len(p.split()) for p in all_text)}")
    
    print("\nFirst 5 paragraphs:")
    for i, para in enumerate(all_text[:5], 1):
        print(f"\n{i}. {para[:200]}{'...' if len(para) > 200 else ''}")
    
    # Save full content
    output_file = 'bmpoa_document_content.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Title: {title}\n")
        f.write("="*50 + "\n\n")
        for para in all_text:
            f.write(para + "\n\n")
    
    print(f"\nFull document saved to: {output_file}")
    
    # Show document structure
    print(f"\nDocument has {len(content)} structural elements")
    
    # Count different element types
    element_types = {}
    for element in content:
        for key in element.keys():
            if key != 'startIndex' and key != 'endIndex':
                element_types[key] = element_types.get(key, 0) + 1
    
    print("\nElement types in document:")
    for elem_type, count in element_types.items():
        print(f"- {elem_type}: {count}")
        
except HttpError as error:
    print(f'\nError accessing document: {error}')
    print("\nPossible solutions:")
    print("1. Make sure you have access to the document")
    print("2. Try running: gcloud auth application-default login --scopes=https://www.googleapis.com/auth/documents.readonly")
    print("3. Or share the document with your Google account")