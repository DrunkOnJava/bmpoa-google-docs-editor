#!/usr/bin/env python3
"""
BMPOA Document Tool - Service Account Version
Full-featured tool for analyzing and editing the BMPOA Google Doc
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constants
DOCUMENT_ID = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
SERVICE_ACCOUNT_KEY = "service-account-key.json"
SCOPES = ['https://www.googleapis.com/auth/documents']

class BMPOADocumentTool:
    def __init__(self):
        self.service = None
        self.document = None
        
    def authenticate(self):
        """Authenticate using service account"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_KEY,
                scopes=SCOPES
            )
            self.service = build('docs', 'v1', credentials=credentials)
            print("✅ Successfully authenticated with service account!")
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def get_document(self, document_id: str = DOCUMENT_ID):
        """Fetch and cache document"""
        try:
            self.document = self.service.documents().get(documentId=document_id).execute()
            return self.document
        except HttpError as e:
            print(f"❌ Error fetching document: {e}")
            return None
    
    def analyze_document(self):
        """Comprehensive document analysis"""
        if not self.document:
            self.get_document()
        
        content = self.document.get('body', {}).get('content', [])
        
        # Initialize counters
        analysis = {
            'title': self.document.get('title', 'Untitled'),
            'paragraphs': 0,
            'tables': 0,
            'lists': 0,
            'total_text': '',
            'headers': [],
            'sections': {},
            'contacts': {
                'emails': [],
                'phones': [],
                'urls': []
            }
        }
        
        # Process content
        for element in content:
            if 'paragraph' in element:
                analysis['paragraphs'] += 1
                paragraph = element['paragraph']
                text = ''
                
                # Extract text
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text += elem['textRun'].get('content', '')
                
                analysis['total_text'] += text
                
                # Check if header (all caps, short)
                if text.strip() and text.strip().isupper() and len(text.strip()) < 100:
                    analysis['headers'].append({
                        'text': text.strip(),
                        'index': element.get('startIndex', 0)
                    })
                
                # Extract contact info
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
                phones = re.findall(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
                urls = re.findall(r'https?://[^\s]+', text)
                
                analysis['contacts']['emails'].extend(emails)
                analysis['contacts']['phones'].extend(phones)
                analysis['contacts']['urls'].extend(urls)
                
            elif 'table' in element:
                analysis['tables'] += 1
            
            elif 'paragraph' in element and element['paragraph'].get('bullet'):
                analysis['lists'] += 1
        
        # Calculate statistics
        words = analysis['total_text'].split()
        analysis['statistics'] = {
            'total_characters': len(analysis['total_text']),
            'total_words': len(words),
            'average_paragraph_length': len(words) / analysis['paragraphs'] if analysis['paragraphs'] > 0 else 0
        }
        
        # Clean up contacts
        analysis['contacts']['emails'] = list(set(analysis['contacts']['emails']))
        analysis['contacts']['phones'] = list(set(analysis['contacts']['phones']))
        analysis['contacts']['urls'] = list(set(analysis['contacts']['urls']))
        
        return analysis
    
    def search_text(self, search_term: str) -> List[Dict]:
        """Find all occurrences of text"""
        if not self.document:
            self.get_document()
        
        content = self.document.get('body', {}).get('content', [])
        occurrences = []
        
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text = elem['textRun'].get('content', '')
                        start_idx = elem.get('startIndex', 0)
                        
                        # Find all occurrences
                        pos = 0
                        while True:
                            pos = text.lower().find(search_term.lower(), pos)
                            if pos == -1:
                                break
                            
                            occurrences.append({
                                'text': text[max(0, pos-20):pos+len(search_term)+20],
                                'start_index': start_idx + pos,
                                'end_index': start_idx + pos + len(search_term)
                            })
                            pos += 1
        
        return occurrences
    
    def replace_text(self, search_text: str, replace_text: str, match_case: bool = False):
        """Replace all occurrences of text"""
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
            print(f"✅ Replaced {occurrences} occurrences of '{search_text}' with '{replace_text}'")
            return occurrences
            
        except HttpError as e:
            print(f"❌ Error replacing text: {e}")
            return 0
    
    def highlight_text(self, search_text: str, color: str = 'yellow'):
        """Highlight all occurrences of text"""
        occurrences = self.search_text(search_text)
        
        if not occurrences:
            print(f"No occurrences of '{search_text}' found")
            return 0
        
        # Color mapping
        colors = {
            'yellow': {'red': 1.0, 'green': 1.0, 'blue': 0.0},
            'red': {'red': 1.0, 'green': 0.0, 'blue': 0.0},
            'green': {'red': 0.0, 'green': 1.0, 'blue': 0.0},
            'blue': {'red': 0.0, 'green': 0.0, 'blue': 1.0},
            'orange': {'red': 1.0, 'green': 0.5, 'blue': 0.0}
        }
        
        rgb_color = colors.get(color, colors['yellow'])
        
        # Create requests
        requests = []
        for occ in occurrences[:50]:  # Limit to 50 for safety
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': occ['start_index'],
                        'endIndex': occ['end_index']
                    },
                    'textStyle': {
                        'backgroundColor': {
                            'color': {'rgbColor': rgb_color}
                        }
                    },
                    'fields': 'backgroundColor'
                }
            })
        
        try:
            self.service.documents().batchUpdate(
                documentId=DOCUMENT_ID,
                body={'requests': requests}
            ).execute()
            
            print(f"✅ Highlighted {len(requests)} occurrences of '{search_text}' in {color}")
            return len(requests)
            
        except HttpError as e:
            print(f"❌ Error highlighting text: {e}")
            return 0
    
    def add_table_of_contents(self):
        """Generate and insert a table of contents"""
        analysis = self.analyze_document()
        headers = analysis['headers']
        
        if not headers:
            print("No headers found to create table of contents")
            return False
        
        # Build TOC text
        toc_text = "TABLE OF CONTENTS\n\n"
        for i, header in enumerate(headers, 1):
            toc_text += f"{i}. {header['text']}\n"
        toc_text += "\n" + "="*50 + "\n\n"
        
        # Insert at beginning
        requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': toc_text
            }
        }]
        
        try:
            self.service.documents().batchUpdate(
                documentId=DOCUMENT_ID,
                body={'requests': requests}
            ).execute()
            
            print(f"✅ Added table of contents with {len(headers)} sections")
            return True
            
        except HttpError as e:
            print(f"❌ Error adding table of contents: {e}")
            return False
    
    def format_headers(self):
        """Format all headers with consistent styling"""
        analysis = self.analyze_document()
        headers = analysis['headers']
        
        if not headers:
            print("No headers found to format")
            return False
        
        requests = []
        for header in headers:
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': header['index'],
                        'endIndex': header['index'] + len(header['text'])
                    },
                    'textStyle': {
                        'bold': True,
                        'fontSize': {
                            'magnitude': 14,
                            'unit': 'PT'
                        }
                    },
                    'fields': 'bold,fontSize'
                }
            })
        
        try:
            self.service.documents().batchUpdate(
                documentId=DOCUMENT_ID,
                body={'requests': requests[:50]}  # Limit for safety
            ).execute()
            
            print(f"✅ Formatted {min(len(requests), 50)} headers")
            return True
            
        except HttpError as e:
            print(f"❌ Error formatting headers: {e}")
            return False
    
    def export_analysis(self, filename: str = 'bmpoa_analysis.json'):
        """Export document analysis to file"""
        analysis = self.analyze_document()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"✅ Analysis exported to {filename}")
        return filename
    
    def generate_report(self):
        """Generate a comprehensive report"""
        analysis = self.analyze_document()
        
        report = []
        report.append(f"BMPOA Document Analysis Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        report.append(f"\nDocument: {analysis['title']}")
        report.append(f"\nStatistics:")
        report.append(f"  - Paragraphs: {analysis['paragraphs']}")
        report.append(f"  - Tables: {analysis['tables']}")
        report.append(f"  - Total Words: {analysis['statistics']['total_words']:,}")
        report.append(f"  - Total Characters: {analysis['statistics']['total_characters']:,}")
        report.append(f"  - Average Paragraph Length: {analysis['statistics']['average_paragraph_length']:.1f} words")
        
        report.append(f"\nSections Found: {len(analysis['headers'])}")
        for i, header in enumerate(analysis['headers'][:20], 1):
            report.append(f"  {i}. {header['text']}")
        
        if analysis['contacts']['emails']:
            report.append(f"\nEmail Addresses:")
            for email in analysis['contacts']['emails']:
                report.append(f"  - {email}")
        
        if analysis['contacts']['phones']:
            report.append(f"\nPhone Numbers:")
            for phone in analysis['contacts']['phones']:
                report.append(f"  - {phone}")
        
        report_text = '\n'.join(report)
        
        with open('bmpoa_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(report_text)
        print(f"\n✅ Report saved to bmpoa_report.txt")
        
        return report_text

def main():
    print("=" * 60)
    print("BMPOA Document Tool - Service Account Version")
    print("=" * 60)
    
    tool = BMPOADocumentTool()
    
    if not tool.authenticate():
        return
    
    # Load and analyze document
    print("\n📄 Loading document...")
    if not tool.get_document():
        return
    
    # Generate report
    print("\n📊 Generating analysis report...")
    tool.generate_report()
    
    # Export full analysis
    tool.export_analysis()
    
    print("\n" + "=" * 60)
    print("Available Operations:")
    print("1. Search for text: tool.search_text('BMPOA')")
    print("2. Replace text: tool.replace_text('old', 'new')")
    print("3. Highlight text: tool.highlight_text('important', 'yellow')")
    print("4. Add table of contents: tool.add_table_of_contents()")
    print("5. Format headers: tool.format_headers()")
    print("\nDocument URL: https://docs.google.com/document/d/" + DOCUMENT_ID)

if __name__ == "__main__":
    main()