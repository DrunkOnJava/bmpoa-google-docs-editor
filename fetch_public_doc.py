#!/usr/bin/env python3
"""
Fetch and analyze the BMPOA Google Doc using web scraping
Since it's publicly viewable, we can analyze its content
"""

import requests
import re
from bs4 import BeautifulSoup
import json

# Document URL
doc_url = "https://docs.google.com/document/d/169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs/export?format=txt"

print("Fetching document content...")

try:
    # Download as plain text
    response = requests.get(doc_url)
    response.raise_for_status()
    
    content = response.text
    
    # Basic analysis
    lines = content.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    print(f"\nDocument Statistics:")
    print(f"- Total lines: {len(lines)}")
    print(f"- Non-empty lines: {len(non_empty_lines)}")
    print(f"- Total characters: {len(content)}")
    print(f"- Total words: {len(content.split())}")
    
    # Show first portion
    print(f"\nFirst 1000 characters:")
    print("-" * 60)
    print(content[:1000])
    print("-" * 60)
    
    # Save full content
    with open('bmpoa_document.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\nFull document saved to: bmpoa_document.txt")
    
    # Analyze structure
    print("\nDocument Structure Analysis:")
    
    # Look for headers (lines in all caps)
    headers = [line for line in non_empty_lines if line.isupper() and len(line) > 3]
    print(f"\nPotential headers found: {len(headers)}")
    for i, header in enumerate(headers[:10]):
        print(f"  {i+1}. {header}")
    
    # Look for sections
    sections = []
    current_section = None
    
    for line in non_empty_lines:
        if line.isupper() and len(line) > 3:
            if current_section:
                sections.append(current_section)
            current_section = {'title': line, 'content': []}
        elif current_section:
            current_section['content'].append(line)
    
    if current_section:
        sections.append(current_section)
    
    print(f"\nSections identified: {len(sections)}")
    
    # Save structured data
    with open('bmpoa_structure.json', 'w') as f:
        json.dump({
            'statistics': {
                'total_lines': len(lines),
                'non_empty_lines': len(non_empty_lines),
                'total_characters': len(content),
                'total_words': len(content.split()),
                'sections': len(sections)
            },
            'headers': headers,
            'sections': sections[:10]  # First 10 sections for review
        }, f, indent=2)
    
    print("\nStructured data saved to: bmpoa_structure.json")
    
except Exception as e:
    print(f"Error fetching document: {e}")