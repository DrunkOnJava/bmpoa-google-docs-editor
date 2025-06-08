#!/usr/bin/env python3
"""
Work with the BMPOA Google Doc
"""

import json
from google_docs_tool import LLMGoogleDocsTool

# Extract document ID from the URL
doc_url = "https://docs.google.com/document/d/169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs/edit?usp=sharing"
doc_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"

# Initialize the tool
tool = LLMGoogleDocsTool(doc_id)

# Authenticate
print("Authenticating...")
auth_result = tool.authenticate()
print(f"Authentication: {'Success' if auth_result['success'] else 'Failed'}")
if not auth_result['success']:
    print(f"Error: {auth_result['message']}")
    exit(1)

# View document structure
print("\nFetching document...")
doc_view = tool.view_document(format="structured")

if doc_view['success']:
    print(f"\nDocument Title: {doc_view['document_title']}")
    print(f"Total Elements: {doc_view['total_elements']}")
    
    # View content in different format for readability
    print("\nFetching document content as plain text...")
    text_view = tool.view_document(format="plain_text")
    
    if text_view['success']:
        content = text_view['content']
        print(f"\nFirst 500 characters of document:")
        print("-" * 50)
        print(content[:500] + "..." if len(content) > 500 else content)
        print("-" * 50)
        
    # Get statistics
    print("\nGetting document statistics...")
    stats = tool.get_document_statistics()
    if stats['success']:
        print(f"\nDetailed Statistics:")
        print(json.dumps(stats['statistics'], indent=2))
else:
    print(f"Error: {doc_view.get('error', 'Unknown error')}")