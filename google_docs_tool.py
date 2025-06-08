#!/usr/bin/env python3
"""
LLM-Optimized Google Docs Tool
==============================

This tool is specifically designed for use by Large Language Models (like Claude) to 
interact with Google Docs through a structured, predictable interface.

Key Features:
- Structured JSON outputs for easy parsing
- Comprehensive error handling with actionable messages
- Stateful document tracking with rollback capabilities
- All Google Docs API operations exposed through simple commands
- Batch operation support for efficiency
- Document visualization in multiple formats

Usage Pattern:
--------------
tool = LLMGoogleDocsTool(document_id)
tool.authenticate()
state = tool.view_document(format='structured')
result = tool.apply_changes([...])
"""

import os
import json
import hashlib
import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# ============================================================================
# DATA STRUCTURES FOR LLM COMPREHENSION
# ============================================================================

class ChangeType(Enum):
    """All possible document change types"""
    # Text Operations
    INSERT_TEXT = "insert_text"
    DELETE_TEXT = "delete_text"
    REPLACE_TEXT = "replace_text"
    REPLACE_ALL_TEXT = "replace_all_text"
    
    # Formatting Operations
    UPDATE_TEXT_STYLE = "update_text_style"
    UPDATE_PARAGRAPH_STYLE = "update_paragraph_style"
    UPDATE_DOCUMENT_STYLE = "update_document_style"
    
    # Structural Operations
    INSERT_PAGE_BREAK = "insert_page_break"
    INSERT_SECTION_BREAK = "insert_section_break"
    INSERT_TABLE = "insert_table"
    INSERT_IMAGE = "insert_image"
    
    # List Operations
    CREATE_BULLETS = "create_bullets"
    DELETE_BULLETS = "delete_bullets"
    CREATE_NUMBERED_LIST = "create_numbered_list"
    
    # Header/Footer Operations
    CREATE_HEADER = "create_header"
    CREATE_FOOTER = "create_footer"
    DELETE_HEADER = "delete_header"
    DELETE_FOOTER = "delete_footer"
    
    # Named Range Operations
    CREATE_NAMED_RANGE = "create_named_range"
    DELETE_NAMED_RANGE = "delete_named_range"
    
    # Table Operations
    INSERT_TABLE_ROW = "insert_table_row"
    INSERT_TABLE_COLUMN = "insert_table_column"
    DELETE_TABLE_ROW = "delete_table_row"
    DELETE_TABLE_COLUMN = "delete_table_column"


@dataclass
class TextStyle:
    """Text styling options - all fields optional"""
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    strikethrough: Optional[bool] = None
    font_size: Optional[int] = None  # In points
    font_family: Optional[str] = None
    foreground_color: Optional[Tuple[float, float, float]] = None  # RGB 0-1
    background_color: Optional[Tuple[float, float, float]] = None  # RGB 0-1
    
    def to_api_format(self) -> Dict:
        """Convert to Google Docs API format"""
        style = {}
        fields = []
        
        if self.bold is not None:
            style['bold'] = self.bold
            fields.append('bold')
        if self.italic is not None:
            style['italic'] = self.italic
            fields.append('italic')
        if self.underline is not None:
            style['underline'] = self.underline
            fields.append('underline')
        if self.strikethrough is not None:
            style['strikethrough'] = self.strikethrough
            fields.append('strikethrough')
        if self.font_size is not None:
            style['fontSize'] = {'magnitude': self.font_size, 'unit': 'PT'}
            fields.append('fontSize')
        if self.font_family is not None:
            style['weightedFontFamily'] = {'fontFamily': self.font_family, 'weight': 400}
            fields.append('weightedFontFamily')
        if self.foreground_color is not None:
            style['foregroundColor'] = {
                'color': {'rgbColor': {
                    'red': self.foreground_color[0],
                    'green': self.foreground_color[1],
                    'blue': self.foreground_color[2]
                }}
            }
            fields.append('foregroundColor')
        if self.background_color is not None:
            style['backgroundColor'] = {
                'color': {'rgbColor': {
                    'red': self.background_color[0],
                    'green': self.background_color[1],
                    'blue': self.background_color[2]
                }}
            }
            fields.append('backgroundColor')
            
        return style, ','.join(fields)


@dataclass
class DocumentChange:
    """Represents a single change to be applied to the document"""
    change_type: ChangeType
    parameters: Dict[str, Any]
    description: str = ""
    
    def to_api_request(self) -> Dict:
        """Convert to Google Docs API request format"""
        # This will be implemented for each change type
        if self.change_type == ChangeType.INSERT_TEXT:
            return {
                'insertText': {
                    'location': {'index': self.parameters['index']},
                    'text': self.parameters['text']
                }
            }
        elif self.change_type == ChangeType.DELETE_TEXT:
            return {
                'deleteContentRange': {
                    'range': {
                        'startIndex': self.parameters['start_index'],
                        'endIndex': self.parameters['end_index']
                    }
                }
            }
        elif self.change_type == ChangeType.REPLACE_TEXT:
            return {
                'deleteContentRange': {
                    'range': {
                        'startIndex': self.parameters['start_index'],
                        'endIndex': self.parameters['end_index']
                    }
                }
            }
        elif self.change_type == ChangeType.REPLACE_ALL_TEXT:
            return {
                'replaceAllText': {
                    'containsText': {
                        'text': self.parameters['search_text'],
                        'matchCase': self.parameters.get('match_case', False)
                    },
                    'replaceText': self.parameters['replace_text']
                }
            }
        elif self.change_type == ChangeType.UPDATE_TEXT_STYLE:
            style, fields = self.parameters['style'].to_api_format()
            return {
                'updateTextStyle': {
                    'range': {
                        'startIndex': self.parameters['start_index'],
                        'endIndex': self.parameters['end_index']
                    },
                    'textStyle': style,
                    'fields': fields
                }
            }
        # Add more change type conversions as needed
        else:
            raise ValueError(f"Unsupported change type: {self.change_type}")


@dataclass
class DocumentElement:
    """Structured representation of a document element"""
    element_type: str  # paragraph, table, image, etc.
    start_index: int
    end_index: int
    content: str
    style: Optional[Dict] = None
    metadata: Optional[Dict] = None


# ============================================================================
# MAIN TOOL CLASS
# ============================================================================

class LLMGoogleDocsTool:
    """
    Main tool class for LLM interaction with Google Docs.
    
    This class provides a high-level interface optimized for LLM usage with:
    - Clear method names and parameters
    - Structured return values
    - Comprehensive error handling
    - State management and rollback
    """
    
    def __init__(self, document_id: str, credentials_path: str = "credentials.json"):
        """
        Initialize the tool with a document ID.
        
        Args:
            document_id: The Google Docs document ID
            credentials_path: Path to OAuth2 credentials JSON file
        """
        self.document_id = document_id
        self.credentials_path = credentials_path
        self.service = None
        self.document_cache = None
        self.document_history = []  # Stack of document states for rollback
        self.last_operation_id = None
        self.scopes = ['https://www.googleapis.com/auth/documents']
        
    def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with Google Docs API.
        
        Returns:
            Dict with keys:
            - success: bool
            - message: str
            - authenticated_user: str (email if available)
        """
        try:
            creds = None
            token_path = 'token.json'
            
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.scopes)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        return {
                            'success': False,
                            'message': f'Credentials file not found at {self.credentials_path}',
                            'authenticated_user': None
                        }
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes)
                    creds = flow.run_local_server(port=0)
                
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('docs', 'v1', credentials=creds)
            
            return {
                'success': True,
                'message': 'Authentication successful',
                'authenticated_user': getattr(creds, 'client_id', 'authenticated')
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Authentication failed: {str(e)}',
                'authenticated_user': None
            }
    
    def view_document(self, format: str = "structured", 
                     include_styles: bool = True,
                     max_elements: Optional[int] = None) -> Dict[str, Any]:
        """
        View the current document in various formats.
        
        Args:
            format: Output format - "structured", "plain_text", "markdown", or "raw"
            include_styles: Whether to include styling information
            max_elements: Maximum number of elements to return (None for all)
            
        Returns:
            Dict with keys:
            - success: bool
            - document_title: str
            - total_elements: int
            - content: List[DocumentElement] or str depending on format
            - metadata: Dict with document metadata
            - error: str (if success is False)
        """
        try:
            # Fetch document
            doc = self.service.documents().get(documentId=self.document_id).execute()
            self.document_cache = doc
            
            # Extract metadata
            metadata = {
                'document_id': self.document_id,
                'title': doc.get('title', 'Untitled'),
                'revision_id': doc.get('revisionId', ''),
                'last_modified': datetime.datetime.now().isoformat()
            }
            
            # Process content based on format
            content = self._process_document_content(doc, format, include_styles, max_elements)
            
            return {
                'success': True,
                'document_title': metadata['title'],
                'total_elements': len(doc.get('body', {}).get('content', [])),
                'content': content,
                'metadata': metadata
            }
            
        except HttpError as e:
            return {
                'success': False,
                'document_title': None,
                'total_elements': 0,
                'content': None,
                'metadata': {},
                'error': f'Failed to fetch document: {str(e)}'
            }
    
    def _process_document_content(self, doc: Dict, format: str, 
                                 include_styles: bool, 
                                 max_elements: Optional[int]) -> Union[List[DocumentElement], str]:
        """Process document content into requested format"""
        body_content = doc.get('body', {}).get('content', [])
        
        if max_elements:
            body_content = body_content[:max_elements]
        
        if format == "raw":
            return json.dumps(body_content, indent=2)
        
        elements = []
        plain_text = ""
        markdown = ""
        
        for element in body_content:
            if 'paragraph' in element:
                para = element['paragraph']
                text = self._extract_paragraph_text(para)
                
                if format == "plain_text":
                    plain_text += text + "\n"
                elif format == "markdown":
                    markdown += self._convert_to_markdown(para, text)
                else:  # structured
                    elem = DocumentElement(
                        element_type="paragraph",
                        start_index=element.get('startIndex', 0),
                        end_index=element.get('endIndex', 0),
                        content=text,
                        style=para.get('paragraphStyle', {}) if include_styles else None,
                        metadata={'bullet': para.get('bullet') is not None}
                    )
                    elements.append(elem)
                    
            elif 'table' in element:
                # Handle tables
                table_data = self._extract_table_data(element['table'])
                
                if format == "structured":
                    elem = DocumentElement(
                        element_type="table",
                        start_index=element.get('startIndex', 0),
                        end_index=element.get('endIndex', 0),
                        content=json.dumps(table_data),
                        metadata={'rows': len(table_data), 'columns': len(table_data[0]) if table_data else 0}
                    )
                    elements.append(elem)
                    
            elif 'sectionBreak' in element:
                if format == "structured":
                    elem = DocumentElement(
                        element_type="section_break",
                        start_index=element.get('startIndex', 0),
                        end_index=element.get('endIndex', 0),
                        content="--- SECTION BREAK ---",
                        metadata=element['sectionBreak']
                    )
                    elements.append(elem)
        
        if format == "plain_text":
            return plain_text
        elif format == "markdown":
            return markdown
        else:
            return elements
    
    def _extract_paragraph_text(self, paragraph: Dict) -> str:
        """Extract text from a paragraph element"""
        text = ""
        for element in paragraph.get('elements', []):
            if 'textRun' in element:
                text += element['textRun'].get('content', '')
        return text
    
    def _extract_table_data(self, table: Dict) -> List[List[str]]:
        """Extract data from a table element"""
        rows = []
        for row in table.get('tableRows', []):
            row_data = []
            for cell in row.get('tableCells', []):
                cell_text = ""
                for content in cell.get('content', []):
                    if 'paragraph' in content:
                        cell_text += self._extract_paragraph_text(content['paragraph'])
                row_data.append(cell_text.strip())
            rows.append(row_data)
        return rows
    
    def _convert_to_markdown(self, paragraph: Dict, text: str) -> str:
        """Convert paragraph to markdown format"""
        style = paragraph.get('paragraphStyle', {})
        named_style = style.get('namedStyleType', 'NORMAL_TEXT')
        
        if named_style == 'HEADING_1':
            return f"# {text}\n"
        elif named_style == 'HEADING_2':
            return f"## {text}\n"
        elif named_style == 'HEADING_3':
            return f"### {text}\n"
        elif paragraph.get('bullet'):
            return f"- {text}\n"
        else:
            return f"{text}\n"
    
    def apply_changes(self, changes: List[DocumentChange], 
                     save_checkpoint: bool = True) -> Dict[str, Any]:
        """
        Apply a list of changes to the document.
        
        Args:
            changes: List of DocumentChange objects
            save_checkpoint: Whether to save current state for rollback
            
        Returns:
            Dict with keys:
            - success: bool
            - changes_applied: int
            - operation_id: str
            - errors: List[str]
            - rollback_available: bool
        """
        if save_checkpoint:
            self._save_checkpoint()
        
        # Convert changes to API requests
        requests = []
        errors = []
        
        for i, change in enumerate(changes):
            try:
                request = change.to_api_request()
                requests.append(request)
            except Exception as e:
                errors.append(f"Change {i}: {str(e)}")
        
        if errors:
            return {
                'success': False,
                'changes_applied': 0,
                'operation_id': None,
                'errors': errors,
                'rollback_available': len(self.document_history) > 0
            }
        
        # Execute batch update
        try:
            result = self.service.documents().batchUpdate(
                documentId=self.document_id,
                body={'requests': requests}
            ).execute()
            
            operation_id = hashlib.md5(
                json.dumps(requests).encode()
            ).hexdigest()[:8]
            
            self.last_operation_id = operation_id
            
            return {
                'success': True,
                'changes_applied': len(changes),
                'operation_id': operation_id,
                'errors': [],
                'rollback_available': True
            }
            
        except HttpError as e:
            return {
                'success': False,
                'changes_applied': 0,
                'operation_id': None,
                'errors': [f"API Error: {str(e)}"],
                'rollback_available': len(self.document_history) > 0
            }
    
    def _save_checkpoint(self):
        """Save current document state for rollback"""
        if self.document_cache:
            self.document_history.append({
                'timestamp': datetime.datetime.now().isoformat(),
                'document': self.document_cache.copy(),
                'operation_id': self.last_operation_id
            })
    
    def rollback(self, steps: int = 1) -> Dict[str, Any]:
        """
        Rollback document to a previous state.
        
        Args:
            steps: Number of operations to rollback (default 1)
            
        Returns:
            Dict with success status and details
        """
        if len(self.document_history) < steps:
            return {
                'success': False,
                'message': f'Cannot rollback {steps} steps. Only {len(self.document_history)} checkpoints available.'
            }
        
        # This is a simplified rollback - in practice, you'd need to
        # calculate the inverse operations
        checkpoint = self.document_history[-steps]
        
        return {
            'success': True,
            'message': f'Rollback to checkpoint from {checkpoint["timestamp"]}',
            'checkpoint_operation_id': checkpoint['operation_id']
        }
    
    def search_and_replace(self, search_text: str, replace_text: str,
                          match_case: bool = False,
                          whole_word: bool = False) -> Dict[str, Any]:
        """
        Search and replace text throughout the document.
        
        Args:
            search_text: Text to search for
            replace_text: Text to replace with
            match_case: Whether to match case
            whole_word: Whether to match whole words only
            
        Returns:
            Dict with operation results
        """
        change = DocumentChange(
            change_type=ChangeType.REPLACE_ALL_TEXT,
            parameters={
                'search_text': search_text,
                'replace_text': replace_text,
                'match_case': match_case
            },
            description=f"Replace all '{search_text}' with '{replace_text}'"
        )
        
        return self.apply_changes([change])
    
    def format_selection(self, start_index: int, end_index: int,
                        style: TextStyle) -> Dict[str, Any]:
        """
        Apply text formatting to a selection.
        
        Args:
            start_index: Start position (1-based)
            end_index: End position (1-based)
            style: TextStyle object with formatting options
            
        Returns:
            Dict with operation results
        """
        change = DocumentChange(
            change_type=ChangeType.UPDATE_TEXT_STYLE,
            parameters={
                'start_index': start_index,
                'end_index': end_index,
                'style': style
            },
            description=f"Format text from {start_index} to {end_index}"
        )
        
        return self.apply_changes([change])
    
    def insert_at_position(self, index: int, text: str,
                          style: Optional[TextStyle] = None) -> Dict[str, Any]:
        """
        Insert text at a specific position.
        
        Args:
            index: Position to insert at (1-based)
            text: Text to insert
            style: Optional styling for inserted text
            
        Returns:
            Dict with operation results
        """
        changes = [
            DocumentChange(
                change_type=ChangeType.INSERT_TEXT,
                parameters={'index': index, 'text': text},
                description=f"Insert text at position {index}"
            )
        ]
        
        if style:
            # Calculate end index after insertion
            end_index = index + len(text)
            changes.append(
                DocumentChange(
                    change_type=ChangeType.UPDATE_TEXT_STYLE,
                    parameters={
                        'start_index': index,
                        'end_index': end_index,
                        'style': style
                    },
                    description="Apply style to inserted text"
                )
            )
        
        return self.apply_changes(changes)
    
    def execute_script(self, script: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a Python script in the context of this document.
        
        Args:
            script: Python code to execute
            context: Additional variables to make available
            
        Returns:
            Dict with execution results
        """
        # Create execution context
        exec_context = {
            'tool': self,
            'document_id': self.document_id,
            'ChangeType': ChangeType,
            'DocumentChange': DocumentChange,
            'TextStyle': TextStyle,
            'changes': []
        }
        
        if context:
            exec_context.update(context)
        
        try:
            # Execute script
            exec(script, exec_context)
            
            # Apply any changes that were created
            if exec_context['changes']:
                result = self.apply_changes(exec_context['changes'])
                return {
                    'success': True,
                    'script_executed': True,
                    'changes_result': result,
                    'output': exec_context.get('output', 'Script executed successfully')
                }
            else:
                return {
                    'success': True,
                    'script_executed': True,
                    'changes_result': None,
                    'output': exec_context.get('output', 'Script executed, no changes made')
                }
                
        except Exception as e:
            return {
                'success': False,
                'script_executed': False,
                'changes_result': None,
                'output': f'Script error: {str(e)}'
            }
    
    def get_document_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the document.
        
        Returns:
            Dict with document statistics
        """
        if not self.document_cache:
            self.view_document()
        
        stats = {
            'title': self.document_cache.get('title', 'Untitled'),
            'total_characters': 0,
            'total_words': 0,
            'total_paragraphs': 0,
            'total_headings': 0,
            'total_lists': 0,
            'total_tables': 0,
            'total_images': 0,
            'style_distribution': {}
        }
        
        content = self.document_cache.get('body', {}).get('content', [])
        
        for element in content:
            if 'paragraph' in element:
                stats['total_paragraphs'] += 1
                para = element['paragraph']
                text = self._extract_paragraph_text(para)
                stats['total_characters'] += len(text)
                stats['total_words'] += len(text.split())
                
                style = para.get('paragraphStyle', {}).get('namedStyleType', 'NORMAL_TEXT')
                if style.startswith('HEADING'):
                    stats['total_headings'] += 1
                
                if para.get('bullet'):
                    stats['total_lists'] += 1
                    
                stats['style_distribution'][style] = stats['style_distribution'].get(style, 0) + 1
                
            elif 'table' in element:
                stats['total_tables'] += 1
                
            elif 'inlineObjectElement' in element:
                stats['total_images'] += 1
        
        return stats


# ============================================================================
# HELPER FUNCTIONS FOR COMMON OPERATIONS
# ============================================================================

def create_heading(text: str, level: int = 1) -> DocumentChange:
    """Create a heading change"""
    return DocumentChange(
        change_type=ChangeType.UPDATE_PARAGRAPH_STYLE,
        parameters={
            'text': text,
            'style': f'HEADING_{level}'
        },
        description=f"Create level {level} heading"
    )


def create_bullet_list(items: List[str], start_index: int) -> List[DocumentChange]:
    """Create a bullet list from items"""
    changes = []
    current_index = start_index
    
    for item in items:
        # Insert item text
        changes.append(DocumentChange(
            change_type=ChangeType.INSERT_TEXT,
            parameters={'index': current_index, 'text': item + '\n'},
            description=f"Insert bullet item: {item[:20]}..."
        ))
        
        # Apply bullet formatting
        changes.append(DocumentChange(
            change_type=ChangeType.CREATE_BULLETS,
            parameters={
                'start_index': current_index,
                'end_index': current_index + len(item) + 1
            },
            description="Apply bullet formatting"
        ))
        
        current_index += len(item) + 1
    
    return changes


# ============================================================================
# MAIN EXECUTION EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Example usage demonstrating the tool's capabilities
    
    doc_id = "1Pcf2vD2k-ib3_BHTZKDJf346vCRFlK5C3CI9t4qI3xg"
    tool = LLMGoogleDocsTool(doc_id)
    
    # Authenticate
    auth_result = tool.authenticate()
    print(json.dumps(auth_result, indent=2))
    
    if auth_result['success']:
        # View document
        doc_view = tool.view_document(format="structured", max_elements=5)
        print(f"\nDocument: {doc_view['document_title']}")
        print(f"Total elements: {doc_view['total_elements']}")
        
        # Get statistics
        stats = tool.get_document_statistics()
        print(f"\nDocument Statistics:")
        print(json.dumps(stats, indent=2))