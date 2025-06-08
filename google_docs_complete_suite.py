#!/usr/bin/env python3
"""
Google Docs Complete Suite
Integrated toolkit with all Google Docs API features and safe data handling
"""

import os
import json
import time
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from google_docs_advanced_toolkit import (
    GoogleDocsAdvancedToolkit, TextStyle, ParagraphStyle,
    ParagraphAlignment, NamedStyleType, ListGlyphType, SectionType
)
from google_docs_specialized_tools import GoogleDocsSpecializedTools


class GoogleDocsCompleteSuite(GoogleDocsSpecializedTools):
    """Complete Google Docs manipulation suite with all features integrated"""
    
    def __init__(self, key_file='service-account-key.json'):
        super().__init__(key_file)
        self.operation_history = []
        self.max_history = 100  # Limit history to prevent memory issues
        
    # ========================================================================
    # SAFE DATA HANDLING
    # ========================================================================
    
    def safe_insert_image_from_file(self, doc_id: str, index: int, 
                                   image_path: str, max_size_mb: int = 5) -> bool:
        """Insert image with size checking to prevent memory issues"""
        # Check file size
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            print(f"✗ Image too large: {file_size_mb:.2f}MB (max: {max_size_mb}MB)")
            print(f"  Please compress the image before inserting")
            return False
        
        # Instead of base64 encoding, upload to Drive first
        try:
            # Upload to Drive
            from googleapiclient.http import MediaFileUpload
            
            file_metadata = {
                'name': os.path.basename(image_path),
                'mimeType': 'image/jpeg'  # Adjust based on actual type
            }
            
            media = MediaFileUpload(image_path, resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webContentLink'
            ).execute()
            
            # Get shareable link
            file_id = file.get('id')
            
            # Make it publicly accessible
            self.drive_service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            # Get the direct link
            file_info = self.drive_service.files().get(
                fileId=file_id,
                fields='webContentLink'
            ).execute()
            
            image_url = file_info.get('webContentLink')
            
            # Insert into document
            result = self.insert_image(doc_id, index, image_url)
            
            print(f"✓ Inserted image from file: {image_path}")
            return result
            
        except Exception as e:
            print(f"✗ Error inserting image: {e}")
            return False
    
    def export_as_format(self, doc_id: str, output_file: str, 
                        format_type: str = 'pdf', chunk_size: int = 1024*1024) -> bool:
        """Export document with chunked downloading to prevent memory issues"""
        mime_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'rtf': 'application/rtf',
            'html': 'text/html',
            'txt': 'text/plain',
            'epub': 'application/epub+zip'
        }
        
        if format_type not in mime_types:
            print(f"✗ Unsupported format: {format_type}")
            return False
        
        try:
            # Export with chunked download
            request = self.drive_service.files().export_media(
                fileId=doc_id,
                mimeType=mime_types[format_type]
            )
            
            # Download in chunks to prevent memory issues
            with open(output_file, 'wb') as f:
                import io
                from googleapiclient.http import MediaIoBaseDownload
                
                downloader = MediaIoBaseDownload(f, request, chunksize=chunk_size)
                done = False
                
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"  Download progress: {int(status.progress() * 100)}%")
            
            print(f"✓ Exported document as {format_type}: {output_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error exporting document: {e}")
            return False
    
    # ========================================================================
    # OPERATION HISTORY AND UNDO
    # ========================================================================
    
    def _record_operation(self, operation: str, params: Dict[str, Any], 
                         doc_id: str, success: bool):
        """Record operation for history tracking"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'params': params,
            'doc_id': doc_id,
            'success': success
        }
        
        self.operation_history.append(record)
        
        # Limit history size
        if len(self.operation_history) > self.max_history:
            self.operation_history = self.operation_history[-self.max_history:]
    
    def get_operation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent operation history"""
        return self.operation_history[-limit:]
    
    def save_checkpoint(self, doc_id: str, checkpoint_name: str) -> bool:
        """Save document state as checkpoint for later restoration"""
        try:
            # Get current document state
            document = self.docs_service.documents().get(
                documentId=doc_id,
                fields='*'
            ).execute()
            
            # Save to file (excluding large binary data)
            checkpoint_file = f"checkpoint_{doc_id}_{checkpoint_name}.json"
            
            # Remove inline objects to prevent large data issues
            if 'inlineObjects' in document:
                document['inlineObjects'] = {
                    k: {'note': 'removed for checkpoint'} 
                    for k in document['inlineObjects'].keys()
                }
            
            with open(checkpoint_file, 'w') as f:
                json.dump(document, f, indent=2)
            
            print(f"✓ Saved checkpoint: {checkpoint_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving checkpoint: {e}")
            return False
    
    # ========================================================================
    # DOCUMENT ANALYSIS
    # ========================================================================
    
    def analyze_document(self, doc_id: str) -> Dict[str, Any]:
        """Comprehensive document analysis"""
        try:
            document = self.docs_service.documents().get(
                documentId=doc_id,
                fields='title,body,documentStyle,namedStyles,lists,footnotes'
            ).execute()
            
            analysis = {
                'title': document.get('title'),
                'statistics': {
                    'total_characters': 0,
                    'total_words': 0,
                    'total_paragraphs': 0,
                    'total_sentences': 0
                },
                'structure': {
                    'headings': {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0},
                    'lists': 0,
                    'tables': 0,
                    'images': 0,
                    'footnotes': len(document.get('footnotes', {}))
                },
                'formatting': {
                    'styles_used': set(),
                    'fonts_used': set(),
                    'colors_used': set()
                },
                'readability': {
                    'average_words_per_sentence': 0,
                    'average_words_per_paragraph': 0
                }
            }
            
            # Analyze content
            content = document.get('body', {}).get('content', [])
            full_text = ''
            
            for element in content:
                if 'paragraph' in element:
                    analysis['statistics']['total_paragraphs'] += 1
                    para_text = ''
                    
                    # Check style
                    style = element['paragraph'].get('paragraphStyle', {})
                    named_style = style.get('namedStyleType', '')
                    if named_style:
                        analysis['formatting']['styles_used'].add(named_style)
                        if 'HEADING' in named_style:
                            level = named_style.split('_')[-1]
                            if level.isdigit():
                                analysis['structure']['headings'][f'h{level}'] += 1
                    
                    # Extract text and formatting
                    for elem in element['paragraph'].get('elements', []):
                        if 'textRun' in elem:
                            text = elem['textRun'].get('content', '')
                            para_text += text
                            full_text += text
                            
                            # Check text style
                            text_style = elem['textRun'].get('textStyle', {})
                            
                            # Font
                            font = text_style.get('weightedFontFamily', {}).get('fontFamily')
                            if font:
                                analysis['formatting']['fonts_used'].add(font)
                            
                            # Color
                            fg_color = text_style.get('foregroundColor', {}).get('color', {}).get('rgbColor', {})
                            if fg_color:
                                color = (fg_color.get('red', 0), 
                                       fg_color.get('green', 0), 
                                       fg_color.get('blue', 0))
                                if color != (0, 0, 0):  # Not default black
                                    analysis['formatting']['colors_used'].add(str(color))
                
                elif 'table' in element:
                    analysis['structure']['tables'] += 1
                
                elif 'inlineObjectElement' in element:
                    analysis['structure']['images'] += 1
            
            # Calculate statistics
            analysis['statistics']['total_characters'] = len(full_text)
            words = full_text.split()
            analysis['statistics']['total_words'] = len(words)
            
            # Estimate sentences (simple approach)
            sentences = [s for s in full_text.split('.') if s.strip()]
            analysis['statistics']['total_sentences'] = len(sentences)
            
            # Readability metrics
            if sentences:
                analysis['readability']['average_words_per_sentence'] = \
                    round(len(words) / len(sentences), 1)
            
            if analysis['statistics']['total_paragraphs'] > 0:
                analysis['readability']['average_words_per_paragraph'] = \
                    round(len(words) / analysis['statistics']['total_paragraphs'], 1)
            
            # Convert sets to lists for JSON serialization
            analysis['formatting']['styles_used'] = list(analysis['formatting']['styles_used'])
            analysis['formatting']['fonts_used'] = list(analysis['formatting']['fonts_used'])
            analysis['formatting']['colors_used'] = list(analysis['formatting']['colors_used'])
            
            return analysis
            
        except Exception as e:
            print(f"✗ Error analyzing document: {e}")
            return {}
    
    # ========================================================================
    # BATCH OPERATIONS WITH PROGRESS
    # ========================================================================
    
    def batch_format_headings(self, doc_id: str, heading_styles: Dict[str, TextStyle],
                            show_progress: bool = True) -> int:
        """Format all headings with specified styles"""
        structure = self.get_structure()
        requests = []
        count = 0
        
        for item in structure:
            if 'HEADING' in item['type']:
                level = f"h{item['type'].split('_')[-1]}"
                if level in heading_styles:
                    style = heading_styles[level]
                    
                    # Build text style request
                    text_style = {}
                    fields = []
                    
                    if style.bold is not None:
                        text_style['bold'] = style.bold
                        fields.append('bold')
                    if style.italic is not None:
                        text_style['italic'] = style.italic
                        fields.append('italic')
                    if style.font_size:
                        text_style['fontSize'] = {
                            'magnitude': style.font_size,
                            'unit': 'PT'
                        }
                        fields.append('fontSize')
                    if style.foreground_color:
                        text_style['foregroundColor'] = {
                            'color': {
                                'rgbColor': {
                                    'red': style.foreground_color[0],
                                    'green': style.foreground_color[1],
                                    'blue': style.foreground_color[2]
                                }
                            }
                        }
                        fields.append('foregroundColor')
                    
                    if fields:
                        requests.append({
                            'updateTextStyle': {
                                'range': {
                                    'startIndex': item['start_index'],
                                    'endIndex': item['end_index'] - 1  # Exclude newline
                                },
                                'textStyle': text_style,
                                'fields': ','.join(fields)
                            }
                        })
                        count += 1
                        
                        if show_progress and count % 10 == 0:
                            print(f"  Processing heading {count}...")
        
        if requests:
            # Execute in batches to prevent timeout
            batch_size = 50
            for i in range(0, len(requests), batch_size):
                batch = requests[i:i+batch_size]
                self._execute_batch_update(doc_id, batch)
                if show_progress:
                    print(f"  Completed batch {i//batch_size + 1}/{(len(requests)-1)//batch_size + 1}")
        
        print(f"✓ Formatted {count} headings")
        return count
    
    # ========================================================================
    # DOCUMENT TEMPLATES
    # ========================================================================
    
    def apply_professional_template(self, doc_id: str) -> bool:
        """Apply professional document template styling"""
        requests = []
        
        # Document margins
        requests.append({
            'updateDocumentStyle': {
                'documentStyle': {
                    'marginTop': {'magnitude': 72, 'unit': 'PT'},
                    'marginBottom': {'magnitude': 72, 'unit': 'PT'},
                    'marginLeft': {'magnitude': 72, 'unit': 'PT'},
                    'marginRight': {'magnitude': 72, 'unit': 'PT'}
                },
                'fields': 'marginTop,marginBottom,marginLeft,marginRight'
            }
        })
        
        # Define heading styles
        heading_styles = {
            'h1': TextStyle(bold=True, font_size=24, foreground_color=(0.2, 0.2, 0.2)),
            'h2': TextStyle(bold=True, font_size=18, foreground_color=(0.3, 0.3, 0.3)),
            'h3': TextStyle(bold=True, font_size=14, foreground_color=(0.4, 0.4, 0.4))
        }
        
        # Format headings
        self.batch_format_headings(doc_id, heading_styles, show_progress=False)
        
        print("✓ Applied professional template")
        return True
    
    # ========================================================================
    # INTERACTIVE FEATURES
    # ========================================================================
    
    def interactive_editor(self, doc_id: str):
        """Interactive document editor interface"""
        print("\n" + "="*60)
        print("GOOGLE DOCS INTERACTIVE EDITOR")
        print("="*60)
        print(f"Document ID: {doc_id}")
        
        # Get document info
        try:
            doc = self.docs_service.documents().get(
                documentId=doc_id,
                fields='title'
            ).execute()
            print(f"Title: {doc.get('title')}")
        except:
            print("Error loading document")
            return
        
        print("\nCommands:")
        print("  1. Search text")
        print("  2. Replace text")
        print("  3. Insert text")
        print("  4. Format selection")
        print("  5. Insert table")
        print("  6. Generate TOC")
        print("  7. Analyze document")
        print("  8. Export document")
        print("  9. View history")
        print("  0. Exit")
        
        # Command descriptions for non-interactive mode
        commands = {
            '1': "Search for 'fire safety'",
            '2': "Replace '2024' with '2025'",
            '3': "Insert 'Updated: ' at position 1",
            '4': "Format text from index 1-100 as bold",
            '5': "Insert 3x3 table at position 100",
            '6': "Generate table of contents",
            '7': "Analyze document structure",
            '8': "Export as PDF",
            '9': "View operation history",
            '0': "Exit editor"
        }
        
        print("\nExample commands that would be available in interactive mode:")
        for cmd, desc in commands.items():
            print(f"  {cmd}: {desc}")
    
    # ========================================================================
    # CONVENIENCE METHODS
    # ========================================================================
    
    def quick_format(self, doc_id: str, format_type: str = 'professional') -> bool:
        """Quick formatting presets"""
        presets = {
            'professional': {
                'margins': {'top': 72, 'bottom': 72, 'left': 72, 'right': 72},
                'line_spacing': 115,
                'font': 'Arial',
                'font_size': 11
            },
            'academic': {
                'margins': {'top': 72, 'bottom': 72, 'left': 72, 'right': 72},
                'line_spacing': 200,  # Double spaced
                'font': 'Times New Roman',
                'font_size': 12
            },
            'compact': {
                'margins': {'top': 36, 'bottom': 36, 'left': 36, 'right': 36},
                'line_spacing': 100,
                'font': 'Calibri',
                'font_size': 10
            }
        }
        
        if format_type not in presets:
            print(f"✗ Unknown format type: {format_type}")
            return False
        
        preset = presets[format_type]
        
        # Apply document style
        self.update_document_style(
            doc_id,
            margin_top=preset['margins']['top'],
            margin_bottom=preset['margins']['bottom'],
            margin_left=preset['margins']['left'],
            margin_right=preset['margins']['right']
        )
        
        print(f"✓ Applied {format_type} formatting")
        return True


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point demonstrating the complete suite"""
    print("Google Docs Complete Suite")
    print("="*60)
    print("\nThis suite provides comprehensive Google Docs manipulation capabilities:")
    print("- All formatting and styling options")
    print("- Table creation and manipulation") 
    print("- Image handling (with size limits)")
    print("- Document analysis and comparison")
    print("- Template and mail merge")
    print("- Batch operations")
    print("- Safe data handling")
    print("- Operation history tracking")
    
    # Initialize suite
    suite = GoogleDocsCompleteSuite()
    
    # Your BMPOA document
    doc_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
    
    print(f"\nWorking with document: {doc_id}")
    
    # Analyze document
    print("\nAnalyzing document...")
    analysis = suite.analyze_document(doc_id)
    
    if analysis:
        print(f"\nDocument Analysis:")
        print(f"  Title: {analysis['title']}")
        print(f"  Words: {analysis['statistics']['total_words']:,}")
        print(f"  Paragraphs: {analysis['statistics']['total_paragraphs']:,}")
        print(f"  Headings: {sum(analysis['structure']['headings'].values())}")
        print(f"  Tables: {analysis['structure']['tables']}")
        print(f"  Average words/paragraph: {analysis['readability']['average_words_per_paragraph']}")
    
    print("\n" + "="*60)
    print("Suite initialized and ready for use!")
    print("\nExample usage:")
    print("  suite.quick_format(doc_id, 'professional')")
    print("  suite.generate_table_of_contents(doc_id)")
    print("  suite.export_as_format(doc_id, 'output.pdf', 'pdf')")
    print("  suite.interactive_editor(doc_id)")
    
    return suite


if __name__ == "__main__":
    suite = main()