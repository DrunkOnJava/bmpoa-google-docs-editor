#!/usr/bin/env python3
"""
Google Docs Specialized Tools
Advanced tools for specific document manipulation tasks
"""

import re
import json
from typing import List, Dict, Optional, Tuple, Any
from google_docs_advanced_toolkit import (
    GoogleDocsAdvancedToolkit, TextStyle, ParagraphStyle, 
    ParagraphAlignment, NamedStyleType, ListGlyphType
)


class GoogleDocsSpecializedTools(GoogleDocsAdvancedToolkit):
    """Extended toolkit with specialized document manipulation features"""
    
    def __init__(self, key_file='service-account-key.json'):
        super().__init__(key_file)
        
    # ========================================================================
    # TEMPLATE AND MAIL MERGE
    # ========================================================================
    
    def create_template(self, doc_id: str, variables: List[str]) -> Dict[str, Any]:
        """Create a template with placeholder variables"""
        template_info = {
            'document_id': doc_id,
            'variables': {},
            'variable_locations': {}
        }
        
        # Get document content
        document = self.docs_service.documents().get(documentId=doc_id).execute()
        content = document.get('body', {}).get('content', [])
        
        # Find all placeholders matching pattern {{variable}}
        for element in content:
            if 'paragraph' in element:
                para_text = ''
                start_index = element.get('startIndex', 0)
                
                for elem in element['paragraph'].get('elements', []):
                    if 'textRun' in elem:
                        text = elem['textRun'].get('content', '')
                        para_text += text
                
                # Find variables in format {{variable_name}}
                for var in variables:
                    pattern = f'{{{{{var}}}}}'
                    if pattern in para_text:
                        if var not in template_info['variable_locations']:
                            template_info['variable_locations'][var] = []
                        
                        # Find all occurrences
                        for match in re.finditer(re.escape(pattern), para_text):
                            template_info['variable_locations'][var].append({
                                'start': start_index + match.start(),
                                'end': start_index + match.end(),
                                'original_text': pattern
                            })
                        
                        template_info['variables'][var] = None
        
        print(f"✓ Created template with {len(variables)} variables")
        return template_info
    
    def mail_merge(self, template_doc_id: str, data: List[Dict[str, str]], 
                  create_separate_docs: bool = True) -> List[str]:
        """Perform mail merge with template and data"""
        created_docs = []
        
        for i, record in enumerate(data):
            if create_separate_docs:
                # Create a copy for each record
                new_title = f"Merged Document {i+1}"
                new_doc_id = self.copy_document(template_doc_id, new_title)
                if not new_doc_id:
                    continue
            else:
                new_doc_id = template_doc_id
            
            # Replace all variables with values
            requests = []
            for var, value in record.items():
                requests.append({
                    'replaceAllText': {
                        'containsText': {
                            'text': f'{{{{{var}}}}}',
                            'matchCase': True
                        },
                        'replaceText': str(value)
                    }
                })
            
            if requests:
                self._execute_batch_update(new_doc_id, requests)
            
            created_docs.append(new_doc_id)
            
            if not create_separate_docs:
                # If updating single document, break after first record
                break
        
        print(f"✓ Mail merge complete: {len(created_docs)} documents processed")
        return created_docs
    
    # ========================================================================
    # ADVANCED FIND AND REPLACE
    # ========================================================================
    
    def find_and_replace_with_formatting(self, doc_id: str, find_text: str,
                                       replace_text: str, text_style: TextStyle) -> int:
        """Find and replace text while applying formatting"""
        # First, do the replacement
        requests = [{
            'replaceAllText': {
                'containsText': {
                    'text': find_text,
                    'matchCase': True
                },
                'replaceText': replace_text
            }
        }]
        
        try:
            result = self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            count = result['replies'][0]['replaceAllText']['occurrencesChanged']
            
            if count > 0 and text_style:
                # Now find all occurrences of the replaced text and format them
                document = self.docs_service.documents().get(documentId=doc_id).execute()
                format_requests = []
                
                # Search through content
                content = document.get('body', {}).get('content', [])
                for element in content:
                    if 'paragraph' in element:
                        para_text = ''
                        start_index = element.get('startIndex', 0)
                        
                        for elem in element['paragraph'].get('elements', []):
                            if 'textRun' in elem:
                                text = elem['textRun'].get('content', '')
                                para_text += text
                        
                        # Find all occurrences of replaced text
                        for match in re.finditer(re.escape(replace_text), para_text):
                            format_start = start_index + match.start()
                            format_end = start_index + match.end()
                            
                            # Build text style
                            style_dict = {}
                            fields = []
                            
                            if text_style.bold is not None:
                                style_dict['bold'] = text_style.bold
                                fields.append('bold')
                            if text_style.italic is not None:
                                style_dict['italic'] = text_style.italic
                                fields.append('italic')
                            if text_style.font_size:
                                style_dict['fontSize'] = {
                                    'magnitude': text_style.font_size,
                                    'unit': 'PT'
                                }
                                fields.append('fontSize')
                            
                            if fields:
                                format_requests.append({
                                    'updateTextStyle': {
                                        'range': {
                                            'startIndex': format_start,
                                            'endIndex': format_end
                                        },
                                        'textStyle': style_dict,
                                        'fields': ','.join(fields)
                                    }
                                })
                
                if format_requests:
                    self._execute_batch_update(doc_id, format_requests)
            
            print(f"✓ Replaced and formatted {count} occurrences")
            return count
            
        except Exception as e:
            print(f"✗ Error in find and replace: {e}")
            return 0
    
    def regex_replace(self, doc_id: str, pattern: str, replacement: str,
                     case_sensitive: bool = True) -> int:
        """Replace text using regular expressions"""
        # Get document content
        document = self.docs_service.documents().get(documentId=doc_id).execute()
        content_elements = document.get('body', {}).get('content', [])
        
        # Build full text and track positions
        full_text = ''
        element_map = []  # Maps character positions to element indices
        
        for element in content_elements:
            if 'paragraph' in element:
                start_pos = len(full_text)
                para_elements = element['paragraph'].get('elements', [])
                
                for elem in para_elements:
                    if 'textRun' in elem:
                        text = elem['textRun'].get('content', '')
                        full_text += text
                        element_map.append({
                            'start': start_pos,
                            'end': len(full_text),
                            'element_start_index': element.get('startIndex', 0)
                        })
        
        # Find matches
        flags = 0 if case_sensitive else re.IGNORECASE
        matches = list(re.finditer(pattern, full_text, flags))
        
        if not matches:
            print("No matches found")
            return 0
        
        # Build replacement requests (process in reverse to maintain indices)
        requests = []
        for match in reversed(matches):
            # Find the document indices for this match
            match_start = match.start()
            match_end = match.end()
            
            # Convert text position to document index
            doc_start = None
            doc_end = None
            
            for elem_info in element_map:
                if elem_info['start'] <= match_start < elem_info['end']:
                    doc_start = elem_info['element_start_index'] + (match_start - elem_info['start'])
                if elem_info['start'] < match_end <= elem_info['end']:
                    doc_end = elem_info['element_start_index'] + (match_end - elem_info['start'])
            
            if doc_start is not None and doc_end is not None:
                # Delete old text
                requests.append({
                    'deleteContentRange': {
                        'range': {
                            'startIndex': doc_start,
                            'endIndex': doc_end
                        }
                    }
                })
                
                # Insert new text
                new_text = match.expand(replacement)
                requests.append({
                    'insertText': {
                        'location': {'index': doc_start},
                        'text': new_text
                    }
                })
        
        if requests:
            self._execute_batch_update(doc_id, requests)
            print(f"✓ Replaced {len(matches)} matches using regex")
            return len(matches)
        
        return 0
    
    # ========================================================================
    # TABLE OF CONTENTS AND INDEXING
    # ========================================================================
    
    def generate_table_of_contents(self, doc_id: str, max_level: int = 3,
                                  insert_at_index: int = 1) -> bool:
        """Generate a table of contents based on headings"""
        # Get document structure
        structure = self.get_structure()
        
        # Filter headings up to max level
        toc_entries = []
        for item in structure:
            if 'HEADING' in item['type']:
                level = int(item['type'].split('_')[-1])
                if level <= max_level:
                    toc_entries.append({
                        'text': item['text'],
                        'level': level,
                        'index': item['start_index']
                    })
        
        if not toc_entries:
            print("No headings found for table of contents")
            return False
        
        # Build TOC text
        toc_text = "TABLE OF CONTENTS\n\n"
        for entry in toc_entries:
            indent = "  " * (entry['level'] - 1)
            toc_text += f"{indent}{entry['text']}\n"
        toc_text += "\n"
        
        # Insert TOC
        requests = [
            # Insert TOC title with formatting
            {
                'insertText': {
                    'location': {'index': insert_at_index},
                    'text': toc_text
                }
            },
            # Format TOC title
            {
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': insert_at_index,
                        'endIndex': insert_at_index + 19  # Length of "TABLE OF CONTENTS\n"
                    },
                    'paragraphStyle': {
                        'namedStyleType': 'TITLE'
                    },
                    'fields': 'namedStyleType'
                }
            },
            # Add page break after TOC
            {
                'insertPageBreak': {
                    'location': {'index': insert_at_index + len(toc_text)}
                }
            }
        ]
        
        self._execute_batch_update(doc_id, requests)
        print(f"✓ Generated table of contents with {len(toc_entries)} entries")
        return True
    
    def create_index(self, doc_id: str, terms: List[str],
                    insert_at_end: bool = True) -> bool:
        """Create an index of specified terms"""
        # Get document
        document = self.docs_service.documents().get(documentId=doc_id).execute()
        
        # Find all occurrences of terms
        index_entries = {}
        
        for term in terms:
            occurrences = []
            
            # Search through content
            content = document.get('body', {}).get('content', [])
            for element in content:
                if 'paragraph' in element:
                    para_text = ''
                    start_index = element.get('startIndex', 0)
                    
                    for elem in element['paragraph'].get('elements', []):
                        if 'textRun' in elem:
                            text = elem['textRun'].get('content', '')
                            para_text += text
                    
                    # Find term occurrences (case insensitive)
                    for match in re.finditer(re.escape(term), para_text, re.IGNORECASE):
                        occurrences.append(start_index + match.start())
            
            if occurrences:
                index_entries[term] = occurrences
        
        if not index_entries:
            print("No index entries found")
            return False
        
        # Build index text
        index_text = "\n\nINDEX\n\n"
        for term in sorted(index_entries.keys(), key=str.lower):
            # In a real implementation, you'd convert indices to page numbers
            index_text += f"{term}: {len(index_entries[term])} occurrences\n"
        
        # Determine insertion point
        if insert_at_end:
            # Get document end index
            body_content = document.get('body', {}).get('content', [])
            insert_index = body_content[-1].get('endIndex', 1) - 1
        else:
            insert_index = 1
        
        # Insert index
        requests = [
            {
                'insertText': {
                    'location': {'index': insert_index},
                    'text': index_text
                }
            },
            {
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': insert_index + 2,
                        'endIndex': insert_index + 7  # "INDEX"
                    },
                    'paragraphStyle': {
                        'namedStyleType': 'TITLE'
                    },
                    'fields': 'namedStyleType'
                }
            }
        ]
        
        self._execute_batch_update(doc_id, requests)
        print(f"✓ Created index with {len(index_entries)} terms")
        return True
    
    # ========================================================================
    # COMMENT AND SUGGESTION MANAGEMENT
    # ========================================================================
    
    def add_comment(self, doc_id: str, start_index: int, end_index: int,
                   comment_text: str) -> bool:
        """Add a comment to a text range"""
        # Note: Comments API requires different scope and method
        # This is a placeholder showing the structure
        print(f"Comment feature requires additional Drive API scope")
        print(f"Would add comment: '{comment_text}' at range {start_index}-{end_index}")
        return True
    
    def create_suggestion(self, doc_id: str, start_index: int, end_index: int,
                         suggested_text: str) -> bool:
        """Create a suggestion for text change"""
        # Suggestions require document to be in suggestion mode
        requests = [{
            'deleteContentRange': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                }
            }
        }, {
            'insertText': {
                'location': {'index': start_index},
                'text': suggested_text
            }
        }]
        
        # Note: Real suggestions require special mode
        print(f"Suggestion feature requires document in suggestion mode")
        print(f"Would suggest replacing range {start_index}-{end_index} with: '{suggested_text}'")
        return True
    
    # ========================================================================
    # DOCUMENT COMPARISON AND TRACKING
    # ========================================================================
    
    def compare_documents(self, doc_id1: str, doc_id2: str) -> Dict[str, Any]:
        """Compare two documents and find differences"""
        # Get both documents
        doc1 = self.docs_service.documents().get(documentId=doc_id1).execute()
        doc2 = self.docs_service.documents().get(documentId=doc_id2).execute()
        
        # Extract text content
        def extract_text(doc):
            text = []
            for element in doc.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    para_text = ''
                    for elem in element['paragraph'].get('elements', []):
                        if 'textRun' in elem:
                            para_text += elem['textRun'].get('content', '')
                    text.append(para_text.strip())
            return text
        
        text1 = extract_text(doc1)
        text2 = extract_text(doc2)
        
        # Simple comparison (could use difflib for more sophisticated comparison)
        comparison = {
            'doc1_title': doc1.get('title'),
            'doc2_title': doc2.get('title'),
            'doc1_paragraphs': len(text1),
            'doc2_paragraphs': len(text2),
            'identical': text1 == text2,
            'added_paragraphs': [],
            'removed_paragraphs': [],
            'modified_paragraphs': []
        }
        
        # Find differences
        max_len = max(len(text1), len(text2))
        for i in range(max_len):
            if i >= len(text1):
                comparison['added_paragraphs'].append({
                    'index': i,
                    'text': text2[i][:100] + '...' if len(text2[i]) > 100 else text2[i]
                })
            elif i >= len(text2):
                comparison['removed_paragraphs'].append({
                    'index': i,
                    'text': text1[i][:100] + '...' if len(text1[i]) > 100 else text1[i]
                })
            elif text1[i] != text2[i]:
                comparison['modified_paragraphs'].append({
                    'index': i,
                    'original': text1[i][:100] + '...' if len(text1[i]) > 100 else text1[i],
                    'modified': text2[i][:100] + '...' if len(text2[i]) > 100 else text2[i]
                })
        
        print(f"✓ Document comparison complete")
        return comparison
    
    def track_changes(self, doc_id: str, baseline_file: str = None) -> Dict[str, Any]:
        """Track changes in a document since last baseline"""
        current_doc = self.docs_service.documents().get(documentId=doc_id).execute()
        
        # Save current state as baseline if requested
        if baseline_file:
            with open(baseline_file, 'w') as f:
                json.dump(current_doc, f, indent=2)
            print(f"✓ Saved baseline to {baseline_file}")
            return {'status': 'baseline_saved'}
        
        # Load previous baseline if exists
        baseline_path = f"{doc_id}_baseline.json"
        try:
            with open(baseline_path, 'r') as f:
                baseline_doc = json.load(f)
        except FileNotFoundError:
            # No baseline, save current as baseline
            with open(baseline_path, 'w') as f:
                json.dump(current_doc, f, indent=2)
            print(f"✓ Created initial baseline")
            return {'status': 'initial_baseline_created'}
        
        # Compare revision IDs
        changes = {
            'changed': baseline_doc.get('revisionId') != current_doc.get('revisionId'),
            'baseline_revision': baseline_doc.get('revisionId'),
            'current_revision': current_doc.get('revisionId'),
            'title_changed': baseline_doc.get('title') != current_doc.get('title')
        }
        
        if changes['changed']:
            print(f"✓ Document has changed since baseline")
        else:
            print(f"✓ No changes since baseline")
        
        return changes
    
    # ========================================================================
    # AUTOMATION AND SCRIPTING
    # ========================================================================
    
    def execute_script(self, doc_id: str, script: List[Dict[str, Any]]) -> bool:
        """Execute a series of operations defined in a script"""
        print(f"Executing script with {len(script)} operations...")
        
        for i, operation in enumerate(script):
            op_type = operation.get('type')
            params = operation.get('params', {})
            
            print(f"\nOperation {i+1}: {op_type}")
            
            try:
                if op_type == 'insert_text':
                    self.insert_text_with_style(
                        doc_id, 
                        params.get('text', ''),
                        params.get('index', 1),
                        params.get('style')
                    )
                elif op_type == 'replace_text':
                    self.find_and_replace_with_formatting(
                        doc_id,
                        params.get('find', ''),
                        params.get('replace', ''),
                        params.get('style')
                    )
                elif op_type == 'insert_table':
                    self.insert_table(
                        doc_id,
                        params.get('index', 1),
                        params.get('rows', 2),
                        params.get('columns', 2)
                    )
                elif op_type == 'apply_style':
                    self.apply_named_style(
                        doc_id,
                        params.get('start', 1),
                        params.get('end', 2),
                        NamedStyleType[params.get('style', 'NORMAL_TEXT')]
                    )
                elif op_type == 'insert_page_break':
                    self.insert_page_break(doc_id, params.get('index', 1))
                else:
                    print(f"Unknown operation type: {op_type}")
                    
            except Exception as e:
                print(f"Error in operation {i+1}: {e}")
                if not operation.get('continue_on_error', True):
                    return False
        
        print(f"\n✓ Script execution complete")
        return True
    
    def batch_process_documents(self, doc_ids: List[str], 
                              operation: str, params: Dict[str, Any]) -> Dict[str, bool]:
        """Apply the same operation to multiple documents"""
        results = {}
        
        for doc_id in doc_ids:
            print(f"\nProcessing document: {doc_id}")
            try:
                if operation == 'replace_all':
                    success = self._execute_batch_update(doc_id, [{
                        'replaceAllText': {
                            'containsText': {
                                'text': params.get('find', ''),
                                'matchCase': params.get('match_case', True)
                            },
                            'replaceText': params.get('replace', '')
                        }
                    }])
                elif operation == 'update_style':
                    success = self.update_document_style(
                        doc_id,
                        **params
                    )
                elif operation == 'export_pdf':
                    output_file = params.get('output_pattern', '{doc_id}.pdf').format(doc_id=doc_id)
                    success = self.export_as_pdf(doc_id, output_file)
                else:
                    print(f"Unknown operation: {operation}")
                    success = False
                
                results[doc_id] = success
                
            except Exception as e:
                print(f"Error processing {doc_id}: {e}")
                results[doc_id] = False
        
        # Summary
        successful = sum(1 for v in results.values() if v)
        print(f"\n✓ Batch processing complete: {successful}/{len(doc_ids)} successful")
        
        return results


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def demonstrate_specialized_features():
    """Demonstrate specialized Google Docs features"""
    print("Google Docs Specialized Tools Demonstration")
    print("="*60)
    
    # Initialize toolkit
    toolkit = GoogleDocsSpecializedTools()
    
    print("\nSpecialized Features Available:")
    print("-" * 40)
    
    # List specialized features
    features = {
        "Template and Mail Merge": [
            "create_template(doc_id, variables=['name', 'date', 'amount'])",
            "mail_merge(template_id, data_records, create_separate_docs=True)"
        ],
        "Advanced Find and Replace": [
            "find_and_replace_with_formatting(doc_id, find, replace, style)",
            "regex_replace(doc_id, pattern, replacement)"
        ],
        "Document Organization": [
            "generate_table_of_contents(doc_id, max_level=3)",
            "create_index(doc_id, terms=['fire', 'safety', 'emergency'])"
        ],
        "Document Comparison": [
            "compare_documents(doc_id1, doc_id2)",
            "track_changes(doc_id, baseline_file)"
        ],
        "Automation": [
            "execute_script(doc_id, script_operations)",
            "batch_process_documents(doc_ids, operation, params)"
        ]
    }
    
    for category, methods in features.items():
        print(f"\n{category}:")
        for method in methods:
            print(f"  • toolkit.{method}")
    
    # Example: Create a simple automation script
    print("\n\nExample Automation Script:")
    print("-" * 40)
    
    example_script = [
        {
            'type': 'insert_text',
            'params': {
                'text': 'Updated: January 2025\n\n',
                'index': 1,
                'style': TextStyle(bold=True, font_size=14)
            }
        },
        {
            'type': 'replace_text',
            'params': {
                'find': '2024',
                'replace': '2025',
                'style': TextStyle(bold=True, foreground_color=(1, 0, 0))
            }
        },
        {
            'type': 'insert_page_break',
            'params': {'index': 100}
        }
    ]
    
    print("Script operations:")
    for op in example_script:
        print(f"  - {op['type']}: {op['params']}")
    
    print("\n" + "="*60)
    print("Specialized toolkit ready for use!")
    
    return toolkit


if __name__ == "__main__":
    toolkit = demonstrate_specialized_features()