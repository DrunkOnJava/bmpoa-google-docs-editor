#!/usr/bin/env python3
"""
Google Docs Advanced Toolkit
Comprehensive toolkit covering all Google Docs API features
"""

import json
import base64
import requests
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class ParagraphAlignment(Enum):
    """Paragraph alignment options"""
    START = "START"
    CENTER = "CENTER"
    END = "END"
    JUSTIFIED = "JUSTIFIED"


class NamedStyleType(Enum):
    """Document style types"""
    NORMAL_TEXT = "NORMAL_TEXT"
    TITLE = "TITLE"
    SUBTITLE = "SUBTITLE"
    HEADING_1 = "HEADING_1"
    HEADING_2 = "HEADING_2"
    HEADING_3 = "HEADING_3"
    HEADING_4 = "HEADING_4"
    HEADING_5 = "HEADING_5"
    HEADING_6 = "HEADING_6"


class ListGlyphType(Enum):
    """List style types"""
    BULLET = "GLYPH_TYPE_UNSPECIFIED"
    DECIMAL = "DECIMAL"
    ALPHA = "ALPHA"
    ALPHA_UPPER = "ALPHA_UPPER"
    ROMAN = "ROMAN"
    ROMAN_UPPER = "ROMAN_UPPER"


class SectionType(Enum):
    """Section break types"""
    UNDEFINED = "SECTION_TYPE_UNSPECIFIED"
    CONTINUOUS = "CONTINUOUS"
    NEXT_PAGE = "NEXT_PAGE"


@dataclass
class TextStyle:
    """Comprehensive text styling options"""
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    strikethrough: Optional[bool] = None
    small_caps: Optional[bool] = None
    font_family: Optional[str] = None
    font_size: Optional[int] = None  # in points
    foreground_color: Optional[Tuple[float, float, float]] = None  # RGB 0-1
    background_color: Optional[Tuple[float, float, float]] = None  # RGB 0-1
    link_url: Optional[str] = None
    baseline_offset: Optional[str] = None  # SUPERSCRIPT or SUBSCRIPT
    

@dataclass
class ParagraphStyle:
    """Comprehensive paragraph styling options"""
    alignment: Optional[ParagraphAlignment] = None
    line_spacing: Optional[float] = None  # 100 = single, 150 = 1.5x, 200 = double
    space_above: Optional[int] = None  # points
    space_below: Optional[int] = None  # points
    indent_first_line: Optional[int] = None  # points
    indent_start: Optional[int] = None  # points
    indent_end: Optional[int] = None  # points
    keep_lines_together: Optional[bool] = None
    keep_with_next: Optional[bool] = None
    avoid_widow_and_orphan: Optional[bool] = None
    border_top: Optional[Dict] = None
    border_bottom: Optional[Dict] = None
    border_left: Optional[Dict] = None
    border_right: Optional[Dict] = None


@dataclass
class TableStyle:
    """Table styling options"""
    rows: int
    columns: int
    table_column_properties: Optional[List[Dict]] = None
    content_direction: Optional[str] = None  # LTR or RTL


# ============================================================================
# MAIN TOOLKIT CLASS
# ============================================================================

class GoogleDocsAdvancedToolkit:
    """Comprehensive Google Docs API toolkit with all features"""
    
    def __init__(self, key_file='service-account-key.json'):
        self.key_file = key_file
        self.service = None
        self.docs_service = None
        self.drive_service = None
        self._authenticate()
        
    def _authenticate(self):
        """Authenticate with all necessary Google services"""
        SCOPES = [
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/drive.file'
        ]
        
        credentials = service_account.Credentials.from_service_account_file(
            self.key_file, scopes=SCOPES
        )
        
        self.docs_service = build('docs', 'v1', credentials=credentials)
        self.drive_service = build('drive', 'v3', credentials=credentials)
        print("✓ Authenticated with Google Docs and Drive APIs")
    
    # ========================================================================
    # DOCUMENT MANAGEMENT
    # ========================================================================
    
    def create_document(self, title: str) -> str:
        """Create a new Google Doc"""
        try:
            document = self.docs_service.documents().create(
                body={'title': title}
            ).execute()
            
            doc_id = document.get('documentId')
            print(f"✓ Created new document: {title} (ID: {doc_id})")
            return doc_id
            
        except HttpError as e:
            print(f"✗ Error creating document: {e}")
            return None
    
    def copy_document(self, doc_id: str, new_title: str) -> str:
        """Create a copy of an existing document"""
        try:
            copy = self.drive_service.files().copy(
                fileId=doc_id,
                body={'name': new_title}
            ).execute()
            
            new_id = copy.get('id')
            print(f"✓ Created copy: {new_title} (ID: {new_id})")
            return new_id
            
        except HttpError as e:
            print(f"✗ Error copying document: {e}")
            return None
    
    def get_document_metadata(self, doc_id: str) -> Dict:
        """Get comprehensive document metadata"""
        try:
            doc = self.docs_service.documents().get(
                documentId=doc_id,
                fields='*'  # Get all fields
            ).execute()
            
            metadata = {
                'title': doc.get('title'),
                'documentId': doc.get('documentId'),
                'revisionId': doc.get('revisionId'),
                'suggestionsViewMode': doc.get('suggestionsViewMode'),
                'documentStyle': doc.get('documentStyle'),
                'namedStyles': doc.get('namedStyles'),
                'lists': doc.get('lists'),
                'namedRanges': doc.get('namedRanges'),
                'positionedObjects': doc.get('positionedObjects'),
                'inlineObjects': doc.get('inlineObjects'),
                'footnotes': doc.get('footnotes'),
                'headers': doc.get('headers'),
                'footers': doc.get('footers')
            }
            
            return metadata
            
        except HttpError as e:
            print(f"✗ Error getting metadata: {e}")
            return {}
    
    # ========================================================================
    # TEXT OPERATIONS
    # ========================================================================
    
    def insert_text_with_style(self, doc_id: str, text: str, index: int, 
                               style: TextStyle = None) -> bool:
        """Insert text with comprehensive styling"""
        requests = []
        
        # Insert text
        requests.append({
            'insertText': {
                'location': {'index': index},
                'text': text
            }
        })
        
        # Apply styling if provided
        if style:
            text_style = {}
            fields = []
            
            if style.bold is not None:
                text_style['bold'] = style.bold
                fields.append('bold')
                
            if style.italic is not None:
                text_style['italic'] = style.italic
                fields.append('italic')
                
            if style.underline is not None:
                text_style['underline'] = style.underline
                fields.append('underline')
                
            if style.strikethrough is not None:
                text_style['strikethrough'] = style.strikethrough
                fields.append('strikethrough')
                
            if style.small_caps is not None:
                text_style['smallCaps'] = style.small_caps
                fields.append('smallCaps')
                
            if style.font_family:
                text_style['weightedFontFamily'] = {
                    'fontFamily': style.font_family
                }
                fields.append('weightedFontFamily')
                
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
                
            if style.background_color:
                text_style['backgroundColor'] = {
                    'color': {
                        'rgbColor': {
                            'red': style.background_color[0],
                            'green': style.background_color[1],
                            'blue': style.background_color[2]
                        }
                    }
                }
                fields.append('backgroundColor')
                
            if style.link_url:
                text_style['link'] = {'url': style.link_url}
                fields.append('link')
                
            if style.baseline_offset:
                text_style['baselineOffset'] = style.baseline_offset
                fields.append('baselineOffset')
            
            if fields:
                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': index,
                            'endIndex': index + len(text)
                        },
                        'textStyle': text_style,
                        'fields': ','.join(fields)
                    }
                })
        
        return self._execute_batch_update(doc_id, requests)
    
    def create_named_range(self, doc_id: str, name: str, start_index: int, 
                          end_index: int) -> str:
        """Create a named range for easy reference"""
        requests = [{
            'createNamedRange': {
                'name': name,
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                }
            }
        }]
        
        try:
            result = self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            range_id = result['replies'][0]['createNamedRange']['namedRangeId']
            print(f"✓ Created named range '{name}' (ID: {range_id})")
            return range_id
            
        except HttpError as e:
            print(f"✗ Error creating named range: {e}")
            return None
    
    # ========================================================================
    # PARAGRAPH OPERATIONS
    # ========================================================================
    
    def format_paragraph(self, doc_id: str, start_index: int, end_index: int,
                        style: ParagraphStyle) -> bool:
        """Apply comprehensive paragraph formatting"""
        paragraph_style = {}
        fields = []
        
        if style.alignment:
            paragraph_style['alignment'] = style.alignment.value
            fields.append('alignment')
            
        if style.line_spacing is not None:
            paragraph_style['lineSpacing'] = style.line_spacing
            fields.append('lineSpacing')
            
        if style.space_above is not None:
            paragraph_style['spaceAbove'] = {
                'magnitude': style.space_above,
                'unit': 'PT'
            }
            fields.append('spaceAbove')
            
        if style.space_below is not None:
            paragraph_style['spaceBelow'] = {
                'magnitude': style.space_below,
                'unit': 'PT'
            }
            fields.append('spaceBelow')
            
        if style.indent_first_line is not None:
            paragraph_style['indentFirstLine'] = {
                'magnitude': style.indent_first_line,
                'unit': 'PT'
            }
            fields.append('indentFirstLine')
            
        if style.indent_start is not None:
            paragraph_style['indentStart'] = {
                'magnitude': style.indent_start,
                'unit': 'PT'
            }
            fields.append('indentStart')
            
        if style.indent_end is not None:
            paragraph_style['indentEnd'] = {
                'magnitude': style.indent_end,
                'unit': 'PT'
            }
            fields.append('indentEnd')
            
        if style.keep_lines_together is not None:
            paragraph_style['keepLinesTogether'] = style.keep_lines_together
            fields.append('keepLinesTogether')
            
        if style.keep_with_next is not None:
            paragraph_style['keepWithNext'] = style.keep_with_next
            fields.append('keepWithNext')
            
        if style.avoid_widow_and_orphan is not None:
            paragraph_style['avoidWidowAndOrphan'] = style.avoid_widow_and_orphan
            fields.append('avoidWidowAndOrphan')
        
        # Add borders if specified
        for border in ['borderTop', 'borderBottom', 'borderLeft', 'borderRight']:
            border_value = getattr(style, border.lower().replace('border', 'border_'))
            if border_value:
                paragraph_style[border] = border_value
                fields.append(border)
        
        requests = [{
            'updateParagraphStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'paragraphStyle': paragraph_style,
                'fields': ','.join(fields)
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    def apply_named_style(self, doc_id: str, start_index: int, end_index: int,
                         style_type: NamedStyleType) -> bool:
        """Apply a predefined named style to a range"""
        requests = [{
            'updateParagraphStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'paragraphStyle': {
                    'namedStyleType': style_type.value
                },
                'fields': 'namedStyleType'
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    # ========================================================================
    # LIST OPERATIONS
    # ========================================================================
    
    def create_list(self, doc_id: str, start_index: int, end_index: int,
                   glyph_type: ListGlyphType = ListGlyphType.BULLET,
                   nesting_level: int = 0) -> bool:
        """Create a list with specified style"""
        requests = [{
            'createParagraphBullets': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'bulletPreset': glyph_type.value
            }
        }]
        
        # Apply nesting if needed
        if nesting_level > 0:
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'paragraphStyle': {
                        'indentStart': {
                            'magnitude': 18 * (nesting_level + 1),
                            'unit': 'PT'
                        }
                    },
                    'fields': 'indentStart'
                }
            })
        
        return self._execute_batch_update(doc_id, requests)
    
    def delete_list(self, doc_id: str, start_index: int, end_index: int) -> bool:
        """Remove list formatting from a range"""
        requests = [{
            'deleteParagraphBullets': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                }
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    # ========================================================================
    # TABLE OPERATIONS
    # ========================================================================
    
    def insert_table(self, doc_id: str, index: int, rows: int, columns: int,
                    table_style: Optional[TableStyle] = None) -> bool:
        """Insert a table with optional styling"""
        table_request = {
            'insertTable': {
                'location': {'index': index},
                'rows': rows,
                'columns': columns
            }
        }
        
        if table_style and table_style.table_column_properties:
            table_request['insertTable']['tableColumnProperties'] = \
                table_style.table_column_properties
        
        requests = [table_request]
        
        return self._execute_batch_update(doc_id, requests)
    
    def insert_table_row(self, doc_id: str, table_start_index: int,
                        row_index: int, insert_below: bool = True) -> bool:
        """Insert a row in an existing table"""
        requests = [{
            'insertTableRow': {
                'tableCellLocation': {
                    'tableStartLocation': {'index': table_start_index},
                    'rowIndex': row_index,
                    'columnIndex': 0
                },
                'insertBelow': insert_below
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    def insert_table_column(self, doc_id: str, table_start_index: int,
                           column_index: int, insert_right: bool = True) -> bool:
        """Insert a column in an existing table"""
        requests = [{
            'insertTableColumn': {
                'tableCellLocation': {
                    'tableStartLocation': {'index': table_start_index},
                    'rowIndex': 0,
                    'columnIndex': column_index
                },
                'insertRight': insert_right
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    def delete_table_row(self, doc_id: str, table_start_index: int,
                        row_index: int) -> bool:
        """Delete a row from a table"""
        requests = [{
            'deleteTableRow': {
                'tableCellLocation': {
                    'tableStartLocation': {'index': table_start_index},
                    'rowIndex': row_index,
                    'columnIndex': 0
                }
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    def delete_table_column(self, doc_id: str, table_start_index: int,
                           column_index: int) -> bool:
        """Delete a column from a table"""
        requests = [{
            'deleteTableColumn': {
                'tableCellLocation': {
                    'tableStartLocation': {'index': table_start_index},
                    'rowIndex': 0,
                    'columnIndex': column_index
                }
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    def update_table_cell_style(self, doc_id: str, table_start_index: int,
                               row_index: int, column_index: int,
                               background_color: Optional[Tuple[float, float, float]] = None,
                               border_style: Optional[Dict] = None) -> bool:
        """Update table cell styling"""
        style = {}
        fields = []
        
        if background_color:
            style['backgroundColor'] = {
                'color': {
                    'rgbColor': {
                        'red': background_color[0],
                        'green': background_color[1],
                        'blue': background_color[2]
                    }
                }
            }
            fields.append('backgroundColor')
        
        if border_style:
            for border in ['borderTop', 'borderBottom', 'borderLeft', 'borderRight']:
                if border in border_style:
                    style[border] = border_style[border]
                    fields.append(border)
        
        requests = [{
            'updateTableCellStyle': {
                'tableCellLocation': {
                    'tableStartLocation': {'index': table_start_index},
                    'rowIndex': row_index,
                    'columnIndex': column_index
                },
                'tableCellStyle': style,
                'fields': ','.join(fields)
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    # ========================================================================
    # IMAGE AND OBJECT OPERATIONS
    # ========================================================================
    
    def insert_image(self, doc_id: str, index: int, image_url: str,
                    width: Optional[int] = None, height: Optional[int] = None) -> bool:
        """Insert an image from a URL"""
        inline_object_properties = {
            'embeddedObject': {
                'imageProperties': {}
            }
        }
        
        if width or height:
            size = {}
            if width:
                size['width'] = {'magnitude': width, 'unit': 'PT'}
            if height:
                size['height'] = {'magnitude': height, 'unit': 'PT'}
            inline_object_properties['embeddedObject']['size'] = size
        
        requests = [{
            'insertInlineImage': {
                'location': {'index': index},
                'uri': image_url,
                'objectSize': inline_object_properties['embeddedObject'].get('size', {})
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    def insert_page_break(self, doc_id: str, index: int) -> bool:
        """Insert a page break"""
        requests = [{
            'insertPageBreak': {
                'location': {'index': index}
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    def insert_section_break(self, doc_id: str, index: int,
                           section_type: SectionType = SectionType.NEXT_PAGE) -> bool:
        """Insert a section break"""
        requests = [{
            'insertSectionBreak': {
                'location': {'index': index},
                'sectionType': section_type.value
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    def insert_footnote(self, doc_id: str, index: int, footnote_text: str) -> bool:
        """Insert a footnote"""
        requests = [
            {
                'createFootnote': {
                    'location': {'index': index}
                }
            }
        ]
        
        # Execute the create footnote request first
        try:
            result = self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            # Get the footnote ID from the response
            footnote_id = result['replies'][0]['createFootnote']['footnoteId']
            
            # Now insert text into the footnote
            footnote_requests = [{
                'insertText': {
                    'location': {
                        'segmentId': footnote_id,
                        'index': 1  # Footnotes start at index 1
                    },
                    'text': footnote_text
                }
            }]
            
            return self._execute_batch_update(doc_id, footnote_requests)
            
        except HttpError as e:
            print(f"✗ Error inserting footnote: {e}")
            return False
    
    # ========================================================================
    # HEADER AND FOOTER OPERATIONS
    # ========================================================================
    
    def create_header(self, doc_id: str, header_text: str,
                     section_index: int = 0) -> bool:
        """Create a header for the document or section"""
        requests = [
            {
                'createHeader': {
                    'type': 'DEFAULT',
                    'sectionBreakLocation': {'index': section_index}
                }
            }
        ]
        
        try:
            result = self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            # Get header ID
            header_id = result['replies'][0]['createHeader']['headerId']
            
            # Insert text into header
            header_requests = [{
                'insertText': {
                    'location': {
                        'segmentId': header_id,
                        'index': 0
                    },
                    'text': header_text
                }
            }]
            
            return self._execute_batch_update(doc_id, header_requests)
            
        except HttpError as e:
            print(f"✗ Error creating header: {e}")
            return False
    
    def create_footer(self, doc_id: str, footer_text: str,
                     section_index: int = 0) -> bool:
        """Create a footer for the document or section"""
        requests = [
            {
                'createFooter': {
                    'type': 'DEFAULT',
                    'sectionBreakLocation': {'index': section_index}
                }
            }
        ]
        
        try:
            result = self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            # Get footer ID
            footer_id = result['replies'][0]['createFooter']['footerId']
            
            # Insert text into footer
            footer_requests = [{
                'insertText': {
                    'location': {
                        'segmentId': footer_id,
                        'index': 0
                    },
                    'text': footer_text
                }
            }]
            
            return self._execute_batch_update(doc_id, footer_requests)
            
        except HttpError as e:
            print(f"✗ Error creating footer: {e}")
            return False
    
    # ========================================================================
    # DOCUMENT STYLE OPERATIONS
    # ========================================================================
    
    def update_document_style(self, doc_id: str, 
                            margin_top: Optional[int] = None,
                            margin_bottom: Optional[int] = None,
                            margin_left: Optional[int] = None,
                            margin_right: Optional[int] = None,
                            page_size: Optional[Dict] = None,
                            use_custom_header_footer_margins: Optional[bool] = None) -> bool:
        """Update overall document styling"""
        document_style = {}
        fields = []
        
        if margin_top is not None:
            document_style['marginTop'] = {'magnitude': margin_top, 'unit': 'PT'}
            fields.append('marginTop')
            
        if margin_bottom is not None:
            document_style['marginBottom'] = {'magnitude': margin_bottom, 'unit': 'PT'}
            fields.append('marginBottom')
            
        if margin_left is not None:
            document_style['marginLeft'] = {'magnitude': margin_left, 'unit': 'PT'}
            fields.append('marginLeft')
            
        if margin_right is not None:
            document_style['marginRight'] = {'magnitude': margin_right, 'unit': 'PT'}
            fields.append('marginRight')
            
        if page_size:
            document_style['pageSize'] = page_size
            fields.append('pageSize')
            
        if use_custom_header_footer_margins is not None:
            document_style['useCustomHeaderFooterMargins'] = use_custom_header_footer_margins
            fields.append('useCustomHeaderFooterMargins')
        
        requests = [{
            'updateDocumentStyle': {
                'documentStyle': document_style,
                'fields': ','.join(fields)
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    # ========================================================================
    # ADVANCED OPERATIONS
    # ========================================================================
    
    def merge_table_cells(self, doc_id: str, table_start_index: int,
                         row_start: int, row_end: int,
                         column_start: int, column_end: int) -> bool:
        """Merge multiple table cells"""
        requests = [{
            'mergeTableCells': {
                'tableRange': {
                    'tableCellLocation': {
                        'tableStartLocation': {'index': table_start_index},
                        'rowIndex': row_start,
                        'columnIndex': column_start
                    },
                    'rowSpan': row_end - row_start + 1,
                    'columnSpan': column_end - column_start + 1
                }
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    def unmerge_table_cells(self, doc_id: str, table_start_index: int,
                           row_index: int, column_index: int) -> bool:
        """Unmerge previously merged table cells"""
        requests = [{
            'unmergeTableCells': {
                'tableRange': {
                    'tableCellLocation': {
                        'tableStartLocation': {'index': table_start_index},
                        'rowIndex': row_index,
                        'columnIndex': column_index
                    },
                    'rowSpan': 1,
                    'columnSpan': 1
                }
            }
        }]
        
        return self._execute_batch_update(doc_id, requests)
    
    def create_bookmark(self, doc_id: str, position: int) -> str:
        """Create a bookmark at a specific position"""
        requests = [{
            'createNamedRange': {
                'name': f'bookmark_{position}',
                'range': {
                    'startIndex': position,
                    'endIndex': position
                }
            }
        }]
        
        try:
            result = self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            bookmark_id = result['replies'][0]['createNamedRange']['namedRangeId']
            print(f"✓ Created bookmark (ID: {bookmark_id})")
            return bookmark_id
            
        except HttpError as e:
            print(f"✗ Error creating bookmark: {e}")
            return None
    
    def get_all_named_ranges(self, doc_id: str) -> List[Dict]:
        """Get all named ranges (including bookmarks) in the document"""
        try:
            document = self.docs_service.documents().get(
                documentId=doc_id,
                fields='namedRanges'
            ).execute()
            
            named_ranges = []
            for name, ranges in document.get('namedRanges', {}).items():
                for range_data in ranges.get('namedRanges', []):
                    named_ranges.append({
                        'name': name,
                        'id': range_data.get('namedRangeId'),
                        'ranges': range_data.get('ranges', [])
                    })
            
            return named_ranges
            
        except HttpError as e:
            print(f"✗ Error getting named ranges: {e}")
            return []
    
    def replace_named_range_content(self, doc_id: str, range_name: str,
                                   new_content: str) -> bool:
        """Replace content in a named range"""
        # First get the named range
        named_ranges = self.get_all_named_ranges(doc_id)
        target_range = None
        
        for nr in named_ranges:
            if nr['name'] == range_name:
                target_range = nr
                break
        
        if not target_range:
            print(f"✗ Named range '{range_name}' not found")
            return False
        
        # Get the range bounds
        ranges = target_range['ranges']
        if not ranges:
            print(f"✗ Named range '{range_name}' has no ranges")
            return False
        
        # Delete existing content and insert new
        requests = []
        for r in ranges:
            start = r.get('startIndex', 0)
            end = r.get('endIndex', 0)
            
            # Delete existing content
            if end > start:
                requests.append({
                    'deleteContentRange': {
                        'range': {
                            'startIndex': start,
                            'endIndex': end
                        }
                    }
                })
            
            # Insert new content
            requests.append({
                'insertText': {
                    'location': {'index': start},
                    'text': new_content
                }
            })
        
        return self._execute_batch_update(doc_id, requests)
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _execute_batch_update(self, doc_id: str, requests: List[Dict]) -> bool:
        """Execute a batch update request"""
        try:
            result = self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            print(f"✓ Executed {len(requests)} operations successfully")
            return True
            
        except HttpError as e:
            print(f"✗ Error executing batch update: {e}")
            return False
    
    def export_as_pdf(self, doc_id: str, output_file: str) -> bool:
        """Export document as PDF"""
        try:
            # Get file content as PDF
            request = self.drive_service.files().export_media(
                fileId=doc_id,
                mimeType='application/pdf'
            )
            
            # Download the PDF
            import io
            from googleapiclient.http import MediaIoBaseDownload
            
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                
            # Write to file
            with open(output_file, 'wb') as f:
                f.write(fh.getvalue())
                
            print(f"✓ Exported document as PDF: {output_file}")
            return True
            
        except HttpError as e:
            print(f"✗ Error exporting as PDF: {e}")
            return False
    
    def get_revision_history(self, doc_id: str) -> List[Dict]:
        """Get document revision history"""
        try:
            revisions = self.drive_service.revisions().list(
                fileId=doc_id,
                fields='revisions(id,modifiedTime,lastModifyingUser)'
            ).execute()
            
            return revisions.get('revisions', [])
            
        except HttpError as e:
            print(f"✗ Error getting revision history: {e}")
            return []


# ============================================================================
# DEMONSTRATION AND USAGE
# ============================================================================

def demonstrate_advanced_features():
    """Demonstrate advanced Google Docs API features"""
    print("Google Docs Advanced Toolkit Demonstration")
    print("="*60)
    
    # Initialize toolkit
    toolkit = GoogleDocsAdvancedToolkit()
    
    # Example document ID (replace with your actual document)
    doc_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
    
    print("\nAvailable Advanced Features:")
    print("-" * 40)
    
    # List all major feature categories
    features = {
        "Document Management": [
            "create_document(title)",
            "copy_document(doc_id, new_title)",
            "get_document_metadata(doc_id)",
            "export_as_pdf(doc_id, output_file)"
        ],
        "Text Formatting": [
            "insert_text_with_style(doc_id, text, index, style)",
            "create_named_range(doc_id, name, start, end)",
            "replace_named_range_content(doc_id, range_name, new_content)"
        ],
        "Paragraph Formatting": [
            "format_paragraph(doc_id, start, end, style)",
            "apply_named_style(doc_id, start, end, style_type)"
        ],
        "Lists": [
            "create_list(doc_id, start, end, glyph_type, nesting)",
            "delete_list(doc_id, start, end)"
        ],
        "Tables": [
            "insert_table(doc_id, index, rows, columns)",
            "insert_table_row/column(doc_id, table_index, position)",
            "delete_table_row/column(doc_id, table_index, position)",
            "merge_table_cells(doc_id, table_index, row_start, row_end, col_start, col_end)",
            "update_table_cell_style(doc_id, table_index, row, col, style)"
        ],
        "Images and Objects": [
            "insert_image(doc_id, index, image_url, width, height)",
            "insert_page_break(doc_id, index)",
            "insert_section_break(doc_id, index, section_type)",
            "insert_footnote(doc_id, index, footnote_text)"
        ],
        "Headers and Footers": [
            "create_header(doc_id, header_text)",
            "create_footer(doc_id, footer_text)"
        ],
        "Document Styling": [
            "update_document_style(doc_id, margins, page_size)"
        ],
        "Advanced Features": [
            "create_bookmark(doc_id, position)",
            "get_all_named_ranges(doc_id)",
            "get_revision_history(doc_id)"
        ]
    }
    
    for category, methods in features.items():
        print(f"\n{category}:")
        for method in methods:
            print(f"  • toolkit.{method}")
    
    print("\n" + "="*60)
    print("Toolkit initialized and ready for use!")
    
    return toolkit


if __name__ == "__main__":
    toolkit = demonstrate_advanced_features()