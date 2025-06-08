#!/usr/bin/env python3
"""
BMPOA Document Editor - Work with the downloaded Google Doc
"""

import os
import re
from typing import List, Dict, Tuple

class BMPOADocumentEditor:
    def __init__(self):
        self.txt_file = "bmpoa_document.txt"
        self.html_file = "bmpoa_document.html"
        self.docx_file = "bmpoa_document.docx"
        self.content = None
        self.sections = {}
        
    def load_document(self):
        """Load the document content"""
        with open(self.txt_file, 'r', encoding='utf-8') as f:
            self.content = f.read()
        self._parse_sections()
        print(f"✓ Document loaded: {len(self.content)} characters")
        
    def _parse_sections(self):
        """Parse document into sections"""
        lines = self.content.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            # Check for main section headers (Roman numerals)
            if re.match(r'^[IVX]+\.\s+[A-Z\s&]+$', line.strip()):
                if current_section:
                    self.sections[current_section] = '\n'.join(section_content)
                current_section = line.strip()
                section_content = [line]
            elif current_section:
                section_content.append(line)
        
        # Save last section
        if current_section:
            self.sections[current_section] = '\n'.join(section_content)
            
    def view_structure(self):
        """Display document structure"""
        print("\nDocument Structure:")
        print("=" * 50)
        
        # Count words and characters
        words = len(self.content.split())
        chars = len(self.content)
        
        print(f"Total Words: {words:,}")
        print(f"Total Characters: {chars:,}")
        print(f"\nMain Sections ({len(self.sections)}):")
        
        for i, section in enumerate(self.sections.keys(), 1):
            section_content = self.sections[section]
            section_words = len(section_content.split())
            print(f"{i}. {section} ({section_words} words)")
            
    def search(self, query: str) -> List[Tuple[int, str]]:
        """Search for text in document"""
        results = []
        lines = self.content.split('\n')
        query_lower = query.lower()
        
        for i, line in enumerate(lines):
            if query_lower in line.lower():
                results.append((i+1, line.strip()))
                
        return results
    
    def extract_section(self, section_name: str) -> str:
        """Extract a specific section"""
        for key, content in self.sections.items():
            if section_name.lower() in key.lower():
                return content
        return None
    
    def get_contacts(self) -> Dict[str, str]:
        """Extract contact information"""
        contacts = {}
        content = self.extract_section("CONTACTS")
        if content:
            lines = content.split('\n')
            for line in lines:
                # Look for phone numbers
                phone_match = re.search(r'(\d{3}-\d{3}-\d{4})', line)
                if phone_match:
                    # Extract name before phone
                    parts = line.split(phone_match.group(1))
                    if parts[0].strip():
                        name = parts[0].strip().rstrip(':').rstrip('-').strip()
                        contacts[name] = phone_match.group(1)
                        
                # Look for email addresses
                email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)
                if email_match:
                    parts = line.split(email_match.group(1))
                    if parts[0].strip():
                        name = parts[0].strip().rstrip(':').strip()
                        contacts[name] = email_match.group(1)
                        
        return contacts
    
    def create_summary(self) -> str:
        """Create a summary of key information"""
        summary = []
        summary.append("BMPOA QUICK REFERENCE GUIDE")
        summary.append("=" * 40)
        
        # Extract key sections
        important_sections = [
            "EMERGENCY NUMBERS",
            "BOARD OFFICERS",
            "REFUSE COLLECTION",
            "INTERNET SERVICE"
        ]
        
        for section in important_sections:
            results = self.search(section)
            if results:
                summary.append(f"\n{section}:")
                # Get next few lines after the header
                start_line = results[0][0]
                lines = self.content.split('\n')
                for i in range(start_line, min(start_line + 5, len(lines))):
                    if lines[i-1].strip():
                        summary.append(f"  {lines[i-1].strip()}")
                        
        return '\n'.join(summary)
    
    def interactive_mode(self):
        """Interactive editing mode"""
        while True:
            print("\n" + "="*50)
            print("BMPOA Document Editor")
            print("="*50)
            print("1. View document structure")
            print("2. Search document")
            print("3. Extract section")
            print("4. View contacts")
            print("5. Create summary")
            print("6. Export section")
            print("0. Exit")
            
            choice = input("\nEnter choice: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.view_structure()
            elif choice == '2':
                query = input("Search for: ").strip()
                results = self.search(query)
                print(f"\nFound {len(results)} results:")
                for line_num, text in results[:10]:
                    print(f"Line {line_num}: {text[:100]}...")
            elif choice == '3':
                section = input("Section name: ").strip()
                content = self.extract_section(section)
                if content:
                    print(f"\n{content[:500]}...")
                else:
                    print("Section not found")
            elif choice == '4':
                contacts = self.get_contacts()
                print("\nContacts found:")
                for name, info in contacts.items():
                    print(f"  {name}: {info}")
            elif choice == '5':
                summary = self.create_summary()
                print(f"\n{summary}")
            elif choice == '6':
                section = input("Section to export: ").strip()
                content = self.extract_section(section)
                if content:
                    filename = f"export_{section.replace(' ', '_').lower()}.txt"
                    with open(filename, 'w') as f:
                        f.write(content)
                    print(f"Exported to {filename}")

if __name__ == "__main__":
    editor = BMPOADocumentEditor()
    editor.load_document()
    editor.view_structure()
    
    # Show sample search
    print("\nSample search for 'fire':")
    results = editor.search("fire")
    for line_num, text in results[:3]:
        print(f"Line {line_num}: {text[:80]}...")
    
    # Extract contacts
    print("\nExtracting contact information...")
    contacts = editor.get_contacts()
    if contacts:
        print(f"Found {len(contacts)} contacts")
        
    # Ask if user wants interactive mode
    if input("\nEnter interactive mode? (y/n): ").lower() == 'y':
        editor.interactive_mode()