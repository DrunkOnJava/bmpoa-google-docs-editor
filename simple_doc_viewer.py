#!/usr/bin/env python3
"""
Simple BMPOA Document Viewer and Editor
Uses the OAuth credentials you provided
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Document ID
DOCUMENT_ID = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"

# Scopes
SCOPES = ['https://www.googleapis.com/auth/documents']

def authenticate():
    """Authenticate and return service object"""
    creds = None
    
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            # Use local server authentication
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('docs', 'v1', credentials=creds)

def view_document(service, document_id):
    """View document content and structure"""
    try:
        # Retrieve the document
        document = service.documents().get(documentId=document_id).execute()
        
        print(f"\nDocument Title: {document.get('title')}")
        print(f"Document ID: {document_id}")
        
        # Get content
        content = document.get('body', {}).get('content', [])
        
        # Extract text
        text_content = []
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                para_text = ''
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        para_text += elem['textRun'].get('content', '')
                if para_text.strip():
                    text_content.append(para_text.strip())
        
        print(f"\nTotal paragraphs: {len(text_content)}")
        print("\nFirst 5 paragraphs:")
        for i, para in enumerate(text_content[:5], 1):
            print(f"\n{i}. {para[:200]}{'...' if len(para) > 200 else ''}")
        
        return document, text_content
        
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None, []

def find_and_highlight_text(service, document_id, search_text):
    """Find text and prepare batch update to highlight it"""
    try:
        # Get document
        document = service.documents().get(documentId=document_id).execute()
        content = document.get('body', {}).get('content', [])
        
        # Find all occurrences
        requests = []
        occurrences = 0
        
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text = elem['textRun'].get('content', '')
                        start_index = elem.get('startIndex', 0)
                        
                        # Find occurrences
                        pos = 0
                        while True:
                            pos = text.find(search_text, pos)
                            if pos == -1:
                                break
                            
                            # Calculate indices
                            actual_start = start_index + pos
                            actual_end = actual_start + len(search_text)
                            
                            # Create highlight request
                            requests.append({
                                'updateTextStyle': {
                                    'range': {
                                        'startIndex': actual_start,
                                        'endIndex': actual_end
                                    },
                                    'textStyle': {
                                        'backgroundColor': {
                                            'color': {
                                                'rgbColor': {
                                                    'red': 1.0,
                                                    'green': 1.0,
                                                    'blue': 0.0
                                                }
                                            }
                                        },
                                        'bold': True
                                    },
                                    'fields': 'backgroundColor,bold'
                                }
                            })
                            
                            occurrences += 1
                            pos += 1
        
        print(f"\nFound '{search_text}' {occurrences} times")
        
        if requests and occurrences > 0:
            # Limit to first 10 for safety
            if len(requests) > 10:
                requests = requests[:10]
                print(f"Highlighting first 10 occurrences only")
            
            # Execute batch update
            result = service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            print(f"Successfully highlighted {len(requests)} occurrences")
            return True
        
        return False
        
    except HttpError as error:
        print(f'An error occurred: {error}')
        return False

def main():
    print("BMPOA Document Viewer and Editor")
    print("=" * 50)
    
    # Authenticate
    print("\nAuthenticating...")
    service = authenticate()
    
    # View document
    document, text_content = view_document(service, DOCUMENT_ID)
    
    if document:
        # Save full text
        with open('bmpoa_full_text.txt', 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(text_content))
        print(f"\nFull document text saved to: bmpoa_full_text.txt")
        
        # Offer to highlight text
        while True:
            print("\nOptions:")
            print("1. Search and highlight text")
            print("2. View document statistics")
            print("3. Exit")
            
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == '1':
                search_text = input("Enter text to search and highlight: ").strip()
                if search_text:
                    find_and_highlight_text(service, DOCUMENT_ID, search_text)
            
            elif choice == '2':
                total_chars = sum(len(p) for p in text_content)
                total_words = sum(len(p.split()) for p in text_content)
                print(f"\nDocument Statistics:")
                print(f"- Total paragraphs: {len(text_content)}")
                print(f"- Total characters: {total_chars}")
                print(f"- Total words: {total_words}")
                print(f"- Average words per paragraph: {total_words / len(text_content):.1f}")
            
            elif choice == '3':
                print("Exiting...")
                break
            
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()