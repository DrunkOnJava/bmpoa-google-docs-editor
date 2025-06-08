# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Google Docs API toolkit for managing and editing Blue Mountain Property Owners Association (BMPOA) documentation. The project provides full Google Docs API access through a layered architecture with safety features for production use.

## Architecture

The toolkit is organized in three layers:

1. **google_docs_advanced_toolkit.py** - Low-level API wrapper covering all Google Docs formatting, tables, images, and document structure operations
2. **google_docs_specialized_tools.py** - Extends the advanced toolkit with higher-level features like templates, mail merge, regex operations, and document comparison
3. **google_docs_complete_suite.py** - Production-ready integration layer with safe data handling, operation history, and batch processing

Key architectural decisions:
- Service account authentication (not OAuth2) for programmatic access
- Images are uploaded to Google Drive first to avoid base64 memory issues
- All operations return success/failure indicators with error messages
- Batch operations are automatically chunked to prevent timeouts
- Operation history is capped to prevent memory growth

## Essential Commands

```bash
# Activate virtual environment
source gdocs_env/bin/activate

# Run the main BMPOA document editor
python bmpoa_docs_editor.py

# Test authentication
python auth_with_service_account.py

# Run complete suite with all features
python google_docs_complete_suite.py

# Analyze document structure
python analyze_and_edit_doc.py
```

## Authentication Setup

The project uses Google Service Account authentication:
- Service account key: `service-account-key.json`
- Required scopes: Google Docs API and Google Drive API
- The service account email must have editor access to target documents

## Working with the BMPOA Document

The primary document ID is hardcoded in several files:
```python
doc_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
```

This is the BMPOA guide document that most scripts are configured to work with.

## Critical Safety Features

When working with images or large data:
- Use `safe_insert_image_from_file()` instead of direct base64 encoding
- Export operations use chunked downloading to prevent memory issues
- The `max_size_mb` parameter limits image uploads (default 5MB)
- Never store base64 data in memory or variables

## Common Development Patterns

### Using the Complete Suite
```python
from google_docs_complete_suite import GoogleDocsCompleteSuite

suite = GoogleDocsCompleteSuite()
suite.analyze_document(doc_id)
suite.batch_format_headings(doc_id, heading_styles)
suite.export_as_format(doc_id, 'output.pdf', 'pdf')
```

### Batch Operations
All batch operations should use the built-in chunking:
```python
# Operations are automatically chunked in groups of 50
suite.batch_process_documents(doc_ids, 'replace_all', {
    'find': 'old_text',
    'replace': 'new_text'
})
```

### Error Handling
All methods follow this pattern:
```python
try:
    result = self.docs_service.documents().batchUpdate(...)
    return True
except HttpError as e:
    print(f"✗ Error: {e}")
    return False
```

## Testing Changes

When testing document modifications:
1. Use `save_checkpoint()` before major changes
2. Work on a copy of the document first: `copy_document()`
3. Check operation history: `get_operation_history()`
4. The BMPOA document has 787 paragraphs and 8,094 words as baseline