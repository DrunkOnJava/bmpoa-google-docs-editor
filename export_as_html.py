#!/usr/bin/env python3
"""
Export Google Doc as HTML for local editing
Since direct API access is blocked, use the export URL approach
"""

import requests
import os
from urllib.parse import urlparse, parse_qs

# Document URL
doc_url = "https://docs.google.com/document/d/169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs/edit?usp=sharing"

# Extract document ID
parsed = urlparse(doc_url)
doc_id = parsed.path.split('/')[3]

print(f"Document ID: {doc_id}")

# Export URLs for Google Docs
export_urls = {
    'html': f'https://docs.google.com/document/d/{doc_id}/export?format=html',
    'txt': f'https://docs.google.com/document/d/{doc_id}/export?format=txt',
    'docx': f'https://docs.google.com/document/d/{doc_id}/export?format=docx',
    'pdf': f'https://docs.google.com/document/d/{doc_id}/export?format=pdf'
}

print("\nAttempting to download document in various formats...")
print("Note: This works if the document is publicly accessible or you're logged into Google in your browser.")

# Try to download each format
for format_type, url in export_urls.items():
    print(f"\nTrying {format_type} format...")
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        if response.status_code == 200:
            filename = f"bmpoa_document.{format_type}"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✓ Successfully downloaded as {filename}")
            
            # If HTML, also save a cleaned version
            if format_type == 'html':
                # Basic cleaning
                content = response.text
                # Save raw HTML
                with open('bmpoa_document_raw.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Also saved raw HTML as bmpoa_document_raw.html")
        else:
            print(f"✗ Failed to download {format_type} (Status: {response.status_code})")
    except Exception as e:
        print(f"✗ Error downloading {format_type}: {str(e)}")

print("\n" + "="*50)
print("Alternative approach:")
print("1. Open the document in your browser")
print("2. File → Download → Microsoft Word (.docx)")
print("3. Save to this directory")
print("4. We can then work with the local DOCX file")
print("\nOr:")
print("1. File → Make a copy")
print("2. Share → Change to 'Anyone with the link can view'")
print("3. Run this script again")