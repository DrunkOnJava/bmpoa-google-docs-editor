#!/usr/bin/env python3
"""
Enhanced Google Docs API Implementation
Based on 2024 API Documentation and Best Practices
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# API Scopes - Use incremental authorization
SCOPES = {
    'readonly': ['https://www.googleapis.com/auth/documents.readonly'],
    'full': ['https://www.googleapis.com/auth/documents']
}

@dataclass
class TextRange:
    """Represents a text range in the document"""
    start_index: int
    end_index: int
    
@dataclass
class TextStyle:
    """Text formatting options"""
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    font_size: Optional[int] = None
    font_family: Optional[str] = None
    foreground_color: Optional[Dict[str, float]] = None
    background_color: Optional[Dict[str, float]] = None

class RequestType(Enum):
    """Supported batch request types"""
    INSERT_TEXT = "insertText"
    DELETE_CONTENT = "deleteContentRange"
    UPDATE_TEXT_STYLE = "updateTextStyle"
    CREATE_PARAGRAPH_BULLETS = "createParagraphBullets"
    INSERT_PAGE_BREAK = "insertPageBreak"
    CREATE_NAMED_RANGE = "createNamedRange"
    UPDATE_PARAGRAPH_STYLE = "updateParagraphStyle"
    INSERT_TABLE = "insertTable"
    DELETE_TABLE_ROW = "deleteTableRow"
    DELETE_TABLE_COLUMN = "deleteTableColumn"
    REPLACE_ALL_TEXT = "replaceAllText"

class EnhancedGoogleDocsAPI:
    """
    Enhanced Google Docs API wrapper with 2024 best practices
    - Batch operations for efficiency
    - Incremental authorization
    - Atomic consistency with WriteControl
    - UTF-16 index handling
    """
    
    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.document_cache = {}
        self.batch_requests = []
        
    def authenticate(self, scope: str = 'full', use_adc: bool = False) -> Dict[str, Any]:
        """
        Authenticate using OAuth 2.0 or Application Default Credentials
        
        Args:
            scope: 'readonly' or 'full' access
            use_adc: Use Application Default Credentials
            
        Returns:
            Authentication result with status and details
        """
        try:
            creds = None
            
            if use_adc:
                # Use Application Default Credentials
                creds, project = google.auth.default(scopes=SCOPES[scope])
            else:
                # OAuth 2.0 flow
                if os.path.exists(self.token_path):
                    creds = Credentials.from_authorized_user_file(self.token_path, SCOPES[scope])
                
                # Refresh or obtain new credentials
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        if not os.path.exists(self.credentials_path):
                            return {
                                'success': False,
                                'error': f'Credentials file not found: {self.credentials_path}',
                                'instructions': [
                                    '1. Go to https://console.cloud.google.com/apis/credentials',
                                    '2. Create OAuth 2.0 Client ID (Desktop app)',
                                    '3. Download and save as credentials.json'
                                ]
                            }
                        
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, SCOPES[scope])
                        creds = flow.run_local_server(port=0)
                    
                    # Save credentials for next run
                    if not use_adc:
                        with open(self.token_path, 'w') as token:
                            token.write(creds.to_json())
            
            # Build service
            self.service = build('docs', 'v1', credentials=creds)
            
            return {
                'success': True,
                'message': 'Authentication successful',
                'scope': scope,
                'method': 'ADC' if use_adc else 'OAuth2'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve document with caching
        
        Args:
            document_id: Google Docs document ID
            
        Returns:
            Document data or error
        """
        try:
            # Check cache first
            if document_id in self.document_cache:
                return {
                    'success': True,
                    'document': self.document_cache[document_id],
                    'from_cache': True
                }
            
            # Fetch from API
            document = self.service.documents().get(documentId=document_id).execute()
            self.document_cache[document_id] = document
            
            return {
                'success': True,
                'document': document,
                'title': document.get('title', 'Untitled'),
                'revision_id': document.get('revisionId'),
                'from_cache': False
            }
            
        except HttpError as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': e.resp.status
            }
    
    def add_batch_request(self, request_type: RequestType, **kwargs):
        """
        Add a request to the batch queue
        
        Args:
            request_type: Type of request from RequestType enum
            **kwargs: Request-specific parameters
        """
        request = {request_type.value: kwargs}
        self.batch_requests.append(request)
        
        return len(self.batch_requests)
    
    def execute_batch(self, document_id: str, write_control: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute all queued batch requests atomically
        
        Args:
            document_id: Target document ID
            write_control: Optional WriteControl for state consistency
            
        Returns:
            Batch execution result
        """
        if not self.batch_requests:
            return {
                'success': False,
                'error': 'No requests in batch queue'
            }
        
        try:
            body = {'requests': self.batch_requests}
            
            if write_control:
                body['writeControl'] = {'requiredRevisionId': write_control}
            
            result = self.service.documents().batchUpdate(
                documentId=document_id,
                body=body
            ).execute()
            
            # Clear batch queue after successful execution
            executed_count = len(self.batch_requests)
            self.batch_requests = []
            
            # Invalidate cache for this document
            if document_id in self.document_cache:
                del self.document_cache[document_id]
            
            return {
                'success': True,
                'executed_requests': executed_count,
                'document_id': result.get('documentId'),
                'replies': result.get('replies', [])
            }
            
        except HttpError as e:
            return {
                'success': False,
                'error': str(e),
                'pending_requests': len(self.batch_requests)
            }
    
    def insert_text(self, text: str, index: int, segment_id: Optional[str] = None):
        """Queue text insertion request"""
        request = {
            'text': text,
            'location': {'index': index}
        }
        if segment_id:
            request['location']['segmentId'] = segment_id
            
        self.add_batch_request(RequestType.INSERT_TEXT, **request)
    
    def delete_content(self, start_index: int, end_index: int):
        """Queue content deletion request"""
        self.add_batch_request(
            RequestType.DELETE_CONTENT,
            range={'startIndex': start_index, 'endIndex': end_index}
        )
    
    def update_text_style(self, start_index: int, end_index: int, style: TextStyle):
        """Queue text style update request"""
        text_style = {}
        
        if style.bold is not None:
            text_style['bold'] = style.bold
        if style.italic is not None:
            text_style['italic'] = style.italic
        if style.underline is not None:
            text_style['underline'] = style.underline
        if style.font_size is not None:
            text_style['fontSize'] = {'magnitude': style.font_size, 'unit': 'PT'}
        if style.font_family is not None:
            text_style['weightedFontFamily'] = {'fontFamily': style.font_family}
        if style.foreground_color is not None:
            text_style['foregroundColor'] = {'color': {'rgbColor': style.foreground_color}}
        if style.background_color is not None:
            text_style['backgroundColor'] = {'color': {'rgbColor': style.background_color}}
        
        self.add_batch_request(
            RequestType.UPDATE_TEXT_STYLE,
            textStyle=text_style,
            range={'startIndex': start_index, 'endIndex': end_index},
            fields='*'  # Update all specified fields
        )
    
    def replace_all_text(self, search_text: str, replace_text: str, match_case: bool = False):
        """Queue replace all text request"""
        self.add_batch_request(
            RequestType.REPLACE_ALL_TEXT,
            containsText={
                'text': search_text,
                'matchCase': match_case
            },
            replaceText=replace_text
        )
    
    def create_paragraph_bullets(self, start_index: int, end_index: int, 
                                bullet_preset: str = "BULLET_DISC_CIRCLE_SQUARE"):
        """Queue paragraph bullet creation request"""
        self.add_batch_request(
            RequestType.CREATE_PARAGRAPH_BULLETS,
            range={'startIndex': start_index, 'endIndex': end_index},
            bulletPreset=bullet_preset
        )
    
    def insert_table(self, index: int, rows: int, columns: int):
        """Queue table insertion request"""
        self.add_batch_request(
            RequestType.INSERT_TABLE,
            location={'index': index},
            rows=rows,
            columns=columns
        )
    
    def insert_page_break(self, index: int):
        """Queue page break insertion request"""
        self.add_batch_request(
            RequestType.INSERT_PAGE_BREAK,
            location={'index': index}
        )
    
    def find_text_indices(self, document_id: str, search_text: str) -> List[TextRange]:
        """
        Find all occurrences of text in document
        
        Args:
            document_id: Document to search
            search_text: Text to find
            
        Returns:
            List of TextRange objects
        """
        doc_result = self.get_document(document_id)
        if not doc_result['success']:
            return []
        
        document = doc_result['document']
        content = document.get('body', {}).get('content', [])
        
        ranges = []
        
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text = elem['textRun'].get('content', '')
                        start_idx = elem.get('startIndex', 0)
                        
                        # Find all occurrences in this text run
                        search_start = 0
                        while True:
                            pos = text.find(search_text, search_start)
                            if pos == -1:
                                break
                            
                            # Calculate UTF-16 indices
                            text_before = text[:pos]
                            utf16_offset = len(text_before.encode('utf-16-le')) // 2
                            utf16_length = len(search_text.encode('utf-16-le')) // 2
                            
                            ranges.append(TextRange(
                                start_index=start_idx + utf16_offset,
                                end_index=start_idx + utf16_offset + utf16_length
                            ))
                            
                            search_start = pos + 1
        
        return ranges
    
    def extract_document_text(self, document_id: str) -> str:
        """Extract all text content from document"""
        doc_result = self.get_document(document_id)
        if not doc_result['success']:
            return ""
        
        document = doc_result['document']
        content = document.get('body', {}).get('content', [])
        
        text_parts = []
        
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                para_text = ''
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        para_text += elem['textRun'].get('content', '')
                if para_text:
                    text_parts.append(para_text)
            elif 'table' in element:
                # Extract table text
                table = element['table']
                for row in table.get('tableRows', []):
                    for cell in row.get('tableCells', []):
                        for cell_element in cell.get('content', []):
                            if 'paragraph' in cell_element:
                                para = cell_element['paragraph']
                                for elem in para.get('elements', []):
                                    if 'textRun' in elem:
                                        text_parts.append(elem['textRun'].get('content', ''))
        
        return '\n'.join(text_parts)

# Example usage
if __name__ == "__main__":
    # Initialize API
    api = EnhancedGoogleDocsAPI()
    
    # Authenticate
    auth_result = api.authenticate(scope='full')
    print(f"Authentication: {auth_result}")
    
    if auth_result['success']:
        doc_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
        
        # Get document
        doc_result = api.get_document(doc_id)
        if doc_result['success']:
            print(f"\nDocument Title: {doc_result['title']}")
            
            # Example: Find and style text
            ranges = api.find_text_indices(doc_id, "BMPOA")
            print(f"\nFound 'BMPOA' {len(ranges)} times")
            
            # Queue batch operations
            for text_range in ranges[:3]:  # Style first 3 occurrences
                style = TextStyle(bold=True, foreground_color={'red': 0.0, 'green': 0.0, 'blue': 1.0})
                api.update_text_style(text_range.start_index, text_range.end_index, style)
            
            # Execute batch
            if api.batch_requests:
                print(f"\nExecuting {len(api.batch_requests)} batch operations...")
                result = api.execute_batch(doc_id)
                print(f"Batch result: {result}")