# Google Docs Complete API Reference

## Overview

This comprehensive Google Docs API toolkit provides full access to all Google Docs features through three main components:

1. **Advanced Toolkit** (`google_docs_advanced_toolkit.py`) - Core formatting and structure manipulation
2. **Specialized Tools** (`google_docs_specialized_tools.py`) - Template, automation, and analysis features  
3. **Complete Suite** (`google_docs_complete_suite.py`) - Integrated toolkit with safe data handling

## Quick Start

```python
from google_docs_complete_suite import GoogleDocsCompleteSuite

# Initialize
suite = GoogleDocsCompleteSuite()

# Work with document
doc_id = "your-document-id"
suite.analyze_document(doc_id)
suite.quick_format(doc_id, 'professional')
```

## Complete Feature List

### Document Management
- `create_document(title)` - Create new document
- `copy_document(doc_id, new_title)` - Copy existing document
- `get_document_metadata(doc_id)` - Get comprehensive metadata
- `export_as_format(doc_id, output_file, format)` - Export (pdf/docx/html/txt/rtf/epub)
- `get_revision_history(doc_id)` - View document history

### Text Operations
- `insert_text_with_style(doc_id, text, index, style)` - Insert styled text
- `create_named_range(doc_id, name, start, end)` - Create named reference
- `replace_named_range_content(doc_id, range_name, new_content)` - Update named range
- `find_and_replace_with_formatting(doc_id, find, replace, style)` - Replace with formatting
- `regex_replace(doc_id, pattern, replacement)` - Regular expression replacement

### Paragraph Formatting
- `format_paragraph(doc_id, start, end, style)` - Apply paragraph styling
- `apply_named_style(doc_id, start, end, style_type)` - Apply predefined styles
- `batch_format_headings(doc_id, heading_styles)` - Format all headings

### Lists
- `create_list(doc_id, start, end, glyph_type, nesting_level)` - Create lists
- `delete_list(doc_id, start, end)` - Remove list formatting

### Tables
- `insert_table(doc_id, index, rows, columns, style)` - Insert table
- `insert_table_row(doc_id, table_index, row_index, insert_below)` - Add row
- `insert_table_column(doc_id, table_index, column_index, insert_right)` - Add column
- `delete_table_row(doc_id, table_index, row_index)` - Remove row
- `delete_table_column(doc_id, table_index, column_index)` - Remove column
- `merge_table_cells(doc_id, table_index, row_start, row_end, col_start, col_end)` - Merge cells
- `update_table_cell_style(doc_id, table_index, row, col, background_color, border)` - Style cells

### Images and Objects
- `insert_image(doc_id, index, image_url, width, height)` - Insert from URL
- `safe_insert_image_from_file(doc_id, index, image_path, max_size_mb)` - Insert from file with size limit
- `insert_page_break(doc_id, index)` - Insert page break
- `insert_section_break(doc_id, index, section_type)` - Insert section break
- `insert_footnote(doc_id, index, footnote_text)` - Add footnote

### Headers and Footers
- `create_header(doc_id, header_text, section_index)` - Add header
- `create_footer(doc_id, footer_text, section_index)` - Add footer

### Document Styling
- `update_document_style(doc_id, margins, page_size)` - Update page layout
- `apply_professional_template(doc_id)` - Apply professional formatting
- `quick_format(doc_id, format_type)` - Apply format presets (professional/academic/compact)

### Templates and Mail Merge
- `create_template(doc_id, variables)` - Create template with placeholders
- `mail_merge(template_id, data_records, create_separate_docs)` - Perform mail merge

### Document Organization
- `generate_table_of_contents(doc_id, max_level, insert_at_index)` - Generate TOC
- `create_index(doc_id, terms, insert_at_end)` - Create index
- `create_bookmark(doc_id, position)` - Add bookmark
- `get_all_named_ranges(doc_id)` - List all named ranges

### Analysis and Comparison
- `analyze_document(doc_id)` - Comprehensive document analysis
- `compare_documents(doc_id1, doc_id2)` - Compare two documents
- `track_changes(doc_id, baseline_file)` - Track document changes

### Automation
- `execute_script(doc_id, script_operations)` - Run operation scripts
- `batch_process_documents(doc_ids, operation, params)` - Process multiple documents
- `save_checkpoint(doc_id, checkpoint_name)` - Save document state
- `get_operation_history(limit)` - View recent operations

## Data Classes

### TextStyle
```python
TextStyle(
    bold=True,
    italic=False,
    underline=False,
    strikethrough=False,
    small_caps=False,
    font_family="Arial",
    font_size=12,
    foreground_color=(0, 0, 0),  # RGB 0-1
    background_color=(1, 1, 1),  # RGB 0-1
    link_url="https://example.com",
    baseline_offset="SUPERSCRIPT"  # or "SUBSCRIPT"
)
```

### ParagraphStyle
```python
ParagraphStyle(
    alignment=ParagraphAlignment.CENTER,
    line_spacing=150,  # 150 = 1.5x spacing
    space_above=12,    # points
    space_below=12,    # points
    indent_first_line=36,  # points
    indent_start=0,    # points
    indent_end=0,      # points
    keep_lines_together=True,
    keep_with_next=False,
    avoid_widow_and_orphan=True
)
```

## Enums

### ParagraphAlignment
- `START` - Left align (LTR) or Right align (RTL)
- `CENTER` - Center align
- `END` - Right align (LTR) or Left align (RTL)
- `JUSTIFIED` - Justified alignment

### NamedStyleType
- `NORMAL_TEXT` - Normal text
- `TITLE` - Title
- `SUBTITLE` - Subtitle
- `HEADING_1` through `HEADING_6` - Heading levels

### ListGlyphType
- `BULLET` - Bullet list
- `DECIMAL` - Numbered list (1, 2, 3...)
- `ALPHA` - Lowercase letters (a, b, c...)
- `ALPHA_UPPER` - Uppercase letters (A, B, C...)
- `ROMAN` - Roman numerals (i, ii, iii...)
- `ROMAN_UPPER` - Uppercase Roman (I, II, III...)

### SectionType
- `CONTINUOUS` - Continuous section break
- `NEXT_PAGE` - Next page section break

## Safe Data Handling

The toolkit includes safety features to prevent memory issues:

1. **Image Size Limits** - Checks file size before processing
2. **Chunked Downloads** - Exports large documents in chunks
3. **History Limits** - Caps operation history to prevent memory growth
4. **No Base64 Storage** - Uploads images to Drive instead of embedding

## Example Workflows

### Professional Document Formatting
```python
# Apply professional template
suite.apply_professional_template(doc_id)

# Format all headings
heading_styles = {
    'h1': TextStyle(bold=True, font_size=24),
    'h2': TextStyle(bold=True, font_size=18),
    'h3': TextStyle(bold=True, font_size=14)
}
suite.batch_format_headings(doc_id, heading_styles)

# Generate table of contents
suite.generate_table_of_contents(doc_id, max_level=3)

# Export as PDF
suite.export_as_format(doc_id, 'document.pdf', 'pdf')
```

### Mail Merge
```python
# Create template
variables = ['name', 'date', 'amount']
template_info = suite.create_template(doc_id, variables)

# Merge with data
data = [
    {'name': 'John Doe', 'date': '2025-01-01', 'amount': '$100'},
    {'name': 'Jane Smith', 'date': '2025-01-02', 'amount': '$200'}
]
doc_ids = suite.mail_merge(doc_id, data, create_separate_docs=True)
```

### Document Analysis
```python
# Comprehensive analysis
analysis = suite.analyze_document(doc_id)
print(f"Words: {analysis['statistics']['total_words']}")
print(f"Readability: {analysis['readability']['average_words_per_sentence']} words/sentence")

# Compare documents
comparison = suite.compare_documents(doc_id1, doc_id2)
print(f"Documents identical: {comparison['identical']}")
```

## Error Handling

All methods include comprehensive error handling and return boolean success indicators or None on failure. Error messages are printed to console with clear descriptions.

## Performance Considerations

1. **Batch Operations** - Group multiple changes into single API calls
2. **Chunked Processing** - Large operations are automatically chunked
3. **Progress Indicators** - Long operations show progress
4. **History Management** - Operation history is automatically pruned

## Authentication

The toolkit uses Google Service Account authentication. Ensure your service account has:
- Google Docs API access
- Google Drive API access (for images and exports)
- Editor permissions on target documents

## Limitations

1. Comments and suggestions require additional scopes
2. Some operations require document owner permissions
3. Image insertion requires Drive API access
4. Large documents may require chunked processing

---

This toolkit provides comprehensive access to all Google Docs API features with safe data handling, making it suitable for production use with documents of any size.