#!/usr/bin/env python3
"""
BMPOA Document Assistant
Comprehensive tool for analyzing and editing the BMPOA Google Doc
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from collections import Counter

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constants
DOCUMENT_ID = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
SCOPES = ['https://www.googleapis.com/auth/documents']

class BMPOADocumentAssistant:
    def __init__(self):
        self.service = None
        self.document = None
        self.text_content = []
        self.document_structure = []
        
    def authenticate(self):
        """Authenticate with Google Docs API"""
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('docs', 'v1', credentials=creds)
        return True
    
    def load_document(self, document_id: str = DOCUMENT_ID):
        """Load document and extract content"""
        try:
            self.document = self.service.documents().get(documentId=document_id).execute()
            self._extract_content()
            return True
        except HttpError as error:
            print(f'Error loading document: {error}')
            return False
    
    def _extract_content(self):
        """Extract text content and structure from document"""
        content = self.document.get('body', {}).get('content', [])
        self.text_content = []
        self.document_structure = []
        
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                para_text = ''
                para_info = {
                    'type': 'paragraph',
                    'start_index': element.get('startIndex', 0),
                    'end_index': element.get('endIndex', 0),
                    'style': paragraph.get('paragraphStyle', {}),
                    'elements': []
                }
                
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text_run = elem['textRun']
                        text = text_run.get('content', '')
                        para_text += text
                        
                        para_info['elements'].append({
                            'text': text,
                            'start_index': elem.get('startIndex', 0),
                            'end_index': elem.get('endIndex', 0),
                            'style': text_run.get('textStyle', {})
                        })
                
                if para_text.strip():
                    self.text_content.append(para_text.strip())
                    para_info['text'] = para_text
                    self.document_structure.append(para_info)
                    
            elif 'table' in element:
                table_info = {
                    'type': 'table',
                    'start_index': element.get('startIndex', 0),
                    'end_index': element.get('endIndex', 0),
                    'rows': element['table'].get('rows', 0),
                    'columns': element['table'].get('columns', 0)
                }
                self.document_structure.append(table_info)
    
    def analyze_document(self) -> Dict:
        """Comprehensive document analysis"""
        analysis = {
            'title': self.document.get('title', 'Untitled'),
            'statistics': self._get_statistics(),
            'structure': self._analyze_structure(),
            'formatting': self._analyze_formatting(),
            'content_analysis': self._analyze_content(),
            'recommendations': self._generate_recommendations()
        }
        return analysis
    
    def _get_statistics(self) -> Dict:
        """Calculate document statistics"""
        total_chars = sum(len(p) for p in self.text_content)
        words = ' '.join(self.text_content).split()
        
        return {
            'total_paragraphs': len(self.text_content),
            'total_characters': total_chars,
            'total_words': len(words),
            'unique_words': len(set(words)),
            'average_paragraph_length': total_chars / len(self.text_content) if self.text_content else 0,
            'average_words_per_paragraph': len(words) / len(self.text_content) if self.text_content else 0
        }
    
    def _analyze_structure(self) -> Dict:
        """Analyze document structure"""
        headers = []
        regular_paragraphs = []
        tables = []
        
        for item in self.document_structure:
            if item['type'] == 'paragraph':
                # Check if it's a header (all caps, short, etc.)
                text = item.get('text', '').strip()
                if text.isupper() and len(text) < 100:
                    headers.append(text)
                else:
                    regular_paragraphs.append(text)
            elif item['type'] == 'table':
                tables.append(item)
        
        return {
            'headers_count': len(headers),
            'paragraphs_count': len(regular_paragraphs),
            'tables_count': len(tables),
            'headers': headers[:10]  # First 10 headers
        }
    
    def _analyze_formatting(self) -> Dict:
        """Analyze text formatting usage"""
        bold_count = 0
        italic_count = 0
        underline_count = 0
        
        for item in self.document_structure:
            if item['type'] == 'paragraph':
                for element in item.get('elements', []):
                    style = element.get('style', {})
                    if style.get('bold'):
                        bold_count += 1
                    if style.get('italic'):
                        italic_count += 1
                    if style.get('underline'):
                        underline_count += 1
        
        return {
            'bold_usage': bold_count,
            'italic_usage': italic_count,
            'underline_usage': underline_count
        }
    
    def _analyze_content(self) -> Dict:
        """Analyze document content"""
        # Word frequency
        all_text = ' '.join(self.text_content).lower()
        words = re.findall(r'\b\w+\b', all_text)
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be'}
        filtered_words = [w for w in words if w not in common_words and len(w) > 3]
        
        word_freq = Counter(filtered_words)
        
        # Find contact information
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', all_text)
        phones = re.findall(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', all_text)
        urls = re.findall(r'https?://[^\s]+', all_text)
        
        return {
            'most_common_words': word_freq.most_common(20),
            'emails': list(set(emails)),
            'phone_numbers': list(set(phones)),
            'urls': list(set(urls))
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate editing recommendations"""
        recommendations = []
        
        stats = self._get_statistics()
        structure = self._analyze_structure()
        
        # Check document length
        if stats['total_words'] > 10000:
            recommendations.append("Consider breaking the document into multiple sections or separate documents for easier navigation.")
        
        # Check paragraph length
        if stats['average_words_per_paragraph'] > 150:
            recommendations.append("Some paragraphs are quite long. Consider breaking them into smaller paragraphs for better readability.")
        
        # Check structure
        if structure['headers_count'] < 5 and stats['total_paragraphs'] > 50:
            recommendations.append("Add more section headers to improve document organization and navigation.")
        
        # Check for consistency
        content = self._analyze_content()
        if len(set(re.findall(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', ' '.join(self.text_content)))) > 1:
            recommendations.append("Standardize phone number formatting throughout the document.")
        
        return recommendations
    
    def search_and_replace(self, search_text: str, replace_text: str, match_case: bool = False) -> Dict:
        """Search and replace text in the document"""
        requests = [{
            'replaceAllText': {
                'containsText': {
                    'text': search_text,
                    'matchCase': match_case
                },
                'replaceText': replace_text
            }
        }]
        
        try:
            result = self.service.documents().batchUpdate(
                documentId=DOCUMENT_ID,
                body={'requests': requests}
            ).execute()
            
            occurrences = result.get('replies', [{}])[0].get('replaceAllText', {}).get('occurrencesChanged', 0)
            
            return {
                'success': True,
                'occurrences_changed': occurrences
            }
        except HttpError as error:
            return {
                'success': False,
                'error': str(error)
            }
    
    def highlight_text(self, search_text: str, color: Dict[str, float] = None) -> Dict:
        """Highlight all occurrences of text"""
        if color is None:
            color = {'red': 1.0, 'green': 1.0, 'blue': 0.0}  # Yellow by default
        
        # Find all occurrences
        requests = []
        occurrences = 0
        
        for item in self.document_structure:
            if item['type'] == 'paragraph':
                for element in item.get('elements', []):
                    text = element.get('text', '')
                    start_idx = element.get('start_index', 0)
                    
                    # Find occurrences
                    pos = 0
                    while True:
                        pos = text.find(search_text, pos)
                        if pos == -1:
                            break
                        
                        requests.append({
                            'updateTextStyle': {
                                'range': {
                                    'startIndex': start_idx + pos,
                                    'endIndex': start_idx + pos + len(search_text)
                                },
                                'textStyle': {
                                    'backgroundColor': {
                                        'color': {'rgbColor': color}
                                    }
                                },
                                'fields': 'backgroundColor'
                            }
                        })
                        
                        occurrences += 1
                        pos += 1
        
        if requests:
            try:
                self.service.documents().batchUpdate(
                    documentId=DOCUMENT_ID,
                    body={'requests': requests[:50]}  # Limit to 50 for safety
                ).execute()
                
                return {
                    'success': True,
                    'occurrences_highlighted': min(occurrences, 50)
                }
            except HttpError as error:
                return {
                    'success': False,
                    'error': str(error)
                }
        
        return {
            'success': False,
            'error': 'Text not found'
        }
    
    def export_analysis(self, filename: str = 'bmpoa_analysis.json'):
        """Export comprehensive analysis to file"""
        analysis = self.analyze_document()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        
        return filename

def main():
    print("BMPOA Document Assistant")
    print("=" * 60)
    
    assistant = BMPOADocumentAssistant()
    
    print("\nAuthenticating...")
    if not assistant.authenticate():
        print("Authentication failed!")
        return
    
    print("Loading document...")
    if not assistant.load_document():
        print("Failed to load document!")
        return
    
    print("Document loaded successfully!")
    
    # Perform analysis
    print("\nAnalyzing document...")
    analysis = assistant.analyze_document()
    
    print(f"\nDocument: {analysis['title']}")
    print(f"\nStatistics:")
    for key, value in analysis['statistics'].items():
        print(f"  - {key.replace('_', ' ').title()}: {value:,.0f}")
    
    print(f"\nStructure:")
    for key, value in analysis['structure'].items():
        if key != 'headers':
            print(f"  - {key.replace('_', ' ').title()}: {value}")
    
    print(f"\nTop 10 Most Common Terms:")
    for word, count in analysis['content_analysis']['most_common_words'][:10]:
        print(f"  - {word}: {count} times")
    
    print(f"\nRecommendations:")
    for i, rec in enumerate(analysis['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    # Export analysis
    export_file = assistant.export_analysis()
    print(f"\nFull analysis exported to: {export_file}")
    
    # Interactive options
    while True:
        print("\n\nOptions:")
        print("1. Search and replace text")
        print("2. Highlight text")
        print("3. View contact information")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            search = input("Text to search for: ")
            replace = input("Replace with: ")
            if search:
                result = assistant.search_and_replace(search, replace)
                if result['success']:
                    print(f"Replaced {result['occurrences_changed']} occurrences")
                else:
                    print(f"Error: {result.get('error')}")
        
        elif choice == '2':
            search = input("Text to highlight: ")
            if search:
                result = assistant.highlight_text(search)
                if result['success']:
                    print(f"Highlighted {result['occurrences_highlighted']} occurrences")
                else:
                    print(f"Error: {result.get('error')}")
        
        elif choice == '3':
            content = analysis['content_analysis']
            print("\nContact Information:")
            print(f"Emails: {', '.join(content['emails'])}")
            print(f"Phone Numbers: {', '.join(content['phone_numbers'])}")
            print(f"URLs: {', '.join(content['urls'][:5])}")  # First 5 URLs
        
        elif choice == '4':
            break

if __name__ == "__main__":
    main()