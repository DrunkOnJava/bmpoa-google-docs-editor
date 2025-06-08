#!/usr/bin/env python3
"""
BMPOA Google Docs Editor
Full-featured editor for the BMPOA documentation
"""

import json
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class BMPOADocsEditor:
    def __init__(self, key_file='service-account-key.json'):
        """Initialize the editor with service account authentication"""
        self.key_file = key_file
        self.service = None
        self.document = None
        self.doc_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
        
        # Authenticate
        self._authenticate()
        
    def _authenticate(self):
        """Authenticate with service account"""
        SCOPES = ['https://www.googleapis.com/auth/documents']
        
        credentials = service_account.Credentials.from_service_account_file(
            self.key_file, scopes=SCOPES
        )
        
        self.service = build('docs', 'v1', credentials=credentials)
        print("✓ Authenticated with Google Docs API")
        
    def load_document(self):
        """Load the current document"""
        try:
            self.document = self.service.documents().get(
                documentId=self.doc_id
            ).execute()
            
            print(f"✓ Loaded document: {self.document.get('title')}")
            return True
        except HttpError as e:
            print(f"✗ Error loading document: {e}")
            return False
            
    def get_text_content(self):
        """Extract all text content from the document"""
        if not self.document:
            self.load_document()
            
        content = []
        elements = self.document.get('body', {}).get('content', [])
        
        for element in elements:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                text = ''
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text += elem['textRun'].get('content', '')
                if text.strip():
                    content.append(text.strip())
                    
        return content
    
    def search_text(self, query):
        """Search for text in the document"""
        content = self.get_text_content()
        results = []
        
        for i, para in enumerate(content):
            if query.lower() in para.lower():
                results.append({
                    'index': i,
                    'text': para,
                    'preview': para[:200] + '...' if len(para) > 200 else para
                })
                
        return results
    
    def get_structure(self):
        """Get document structure (headings, sections)"""
        if not self.document:
            self.load_document()
            
        structure = []
        elements = self.document.get('body', {}).get('content', [])
        
        for element in elements:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                style = paragraph.get('paragraphStyle', {}).get('namedStyleType', '')
                
                if 'HEADING' in style:
                    text = ''
                    for elem in paragraph.get('elements', []):
                        if 'textRun' in elem:
                            text += elem['textRun'].get('content', '')
                    
                    if text.strip():
                        structure.append({
                            'type': style,
                            'text': text.strip(),
                            'start_index': element.get('startIndex', 0),
                            'end_index': element.get('endIndex', 0)
                        })
                        
        return structure
    
    def replace_text(self, old_text, new_text):
        """Replace text throughout the document"""
        requests = [{
            'replaceAllText': {
                'containsText': {
                    'text': old_text,
                    'matchCase': True
                },
                'replaceText': new_text
            }
        }]
        
        try:
            result = self.service.documents().batchUpdate(
                documentId=self.doc_id,
                body={'requests': requests}
            ).execute()
            
            replies = result.get('replies', [])
            if replies and replies[0].get('replaceAllText'):
                count = replies[0]['replaceAllText']['occurrencesChanged']
                print(f"✓ Replaced {count} occurrences of '{old_text}' with '{new_text}'")
                return count
            else:
                print("No occurrences found")
                return 0
                
        except HttpError as e:
            print(f"✗ Error replacing text: {e}")
            return 0
    
    def insert_text(self, text, index=1):
        """Insert text at a specific index"""
        requests = [{
            'insertText': {
                'location': {
                    'index': index
                },
                'text': text
            }
        }]
        
        try:
            self.service.documents().batchUpdate(
                documentId=self.doc_id,
                body={'requests': requests}
            ).execute()
            
            print(f"✓ Inserted text at index {index}")
            return True
            
        except HttpError as e:
            print(f"✗ Error inserting text: {e}")
            return False
    
    def format_text(self, start_index, end_index, bold=None, italic=None, 
                   font_size=None, color=None):
        """Format text with various styles"""
        text_style = {}
        fields = []
        
        if bold is not None:
            text_style['bold'] = bold
            fields.append('bold')
            
        if italic is not None:
            text_style['italic'] = italic
            fields.append('italic')
            
        if font_size is not None:
            text_style['fontSize'] = {
                'magnitude': font_size,
                'unit': 'PT'
            }
            fields.append('fontSize')
            
        if color is not None:
            text_style['foregroundColor'] = {
                'color': {
                    'rgbColor': {
                        'red': color[0],
                        'green': color[1],
                        'blue': color[2]
                    }
                }
            }
            fields.append('foregroundColor')
        
        requests = [{
            'updateTextStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'textStyle': text_style,
                'fields': ','.join(fields)
            }
        }]
        
        try:
            self.service.documents().batchUpdate(
                documentId=self.doc_id,
                body={'requests': requests}
            ).execute()
            
            print(f"✓ Formatted text from index {start_index} to {end_index}")
            return True
            
        except HttpError as e:
            print(f"✗ Error formatting text: {e}")
            return False
    
    def save_backup(self, filename='document_backup.json'):
        """Save a backup of the current document state"""
        if not self.document:
            self.load_document()
            
        with open(filename, 'w') as f:
            json.dump(self.document, f, indent=2)
            
        print(f"✓ Document backed up to {filename}")
        
    def get_statistics(self):
        """Get document statistics"""
        content = self.get_text_content()
        full_text = ' '.join(content)
        
        stats = {
            'title': self.document.get('title', 'Untitled'),
            'total_paragraphs': len(content),
            'total_words': len(full_text.split()),
            'total_characters': len(full_text),
            'sections': len([h for h in self.get_structure() if h['type'] == 'HEADING_1'])
        }
        
        return stats

def main():
    """Example usage of the BMPOA Docs Editor"""
    print("BMPOA Google Docs Editor")
    print("="*50)
    
    # Initialize editor
    editor = BMPOADocsEditor()
    
    # Load document
    if editor.load_document():
        # Get statistics
        stats = editor.get_statistics()
        print(f"\nDocument Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Show document structure
        print(f"\nDocument Structure:")
        structure = editor.get_structure()
        for item in structure[:10]:  # Show first 10 headings
            indent = "  " * (int(item['type'][-1]) - 1)
            print(f"{indent}{item['text']}")
        
        # Example: Search for fire-related content
        print(f"\nSearching for 'fire'...")
        results = editor.search_text('fire')
        print(f"Found {len(results)} occurrences")
        
        # Save backup
        editor.save_backup('bmpoa_backup.json')
        
        print("\n✅ Editor ready for use!")
        print("\nAvailable methods:")
        print("  - editor.search_text('query')")
        print("  - editor.replace_text('old', 'new')")
        print("  - editor.insert_text('text', index)")
        print("  - editor.format_text(start, end, bold=True)")
        print("  - editor.get_structure()")
        print("  - editor.save_backup()")

if __name__ == "__main__":
    main()