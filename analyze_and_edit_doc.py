#!/usr/bin/env python3
"""
Comprehensive BMPOA Document Analysis and Editing Assistant
"""

import json
import re
from collections import Counter
from typing import List, Dict, Tuple

class BMPOADocumentAnalyzer:
    def __init__(self, content_file='bmpoa_document.txt'):
        """Initialize with the document content"""
        with open(content_file, 'r', encoding='utf-8') as f:
            self.content = f.read()
        self.lines = self.content.split('\n')
        self.sections = self._parse_sections()
        
    def _parse_sections(self) -> List[Dict]:
        """Parse document into structured sections"""
        sections = []
        current_section = None
        current_subsection = None
        
        for line in self.lines:
            line = line.strip()
            if not line:
                continue
                
            # Main section headers (Roman numerals)
            if re.match(r'^[IVX]+\.\s+[A-Z\s&]+$', line):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    'title': line,
                    'level': 1,
                    'subsections': [],
                    'content': []
                }
                current_subsection = None
            # Subsection headers (Letters)
            elif re.match(r'^[A-Z]\.\s+', line) and current_section:
                if current_subsection:
                    current_section['subsections'].append(current_subsection)
                current_subsection = {
                    'title': line,
                    'level': 2,
                    'content': []
                }
            # Content lines
            elif current_subsection:
                current_subsection['content'].append(line)
            elif current_section:
                current_section['content'].append(line)
                
        # Add final section
        if current_subsection and current_section:
            current_section['subsections'].append(current_subsection)
        if current_section:
            sections.append(current_section)
            
        return sections
    
    def get_table_of_contents(self) -> str:
        """Generate a formatted table of contents"""
        toc = "TABLE OF CONTENTS\n" + "="*50 + "\n\n"
        
        for section in self.sections:
            toc += f"{section['title']}\n"
            for subsection in section.get('subsections', []):
                toc += f"    {subsection['title']}\n"
            toc += "\n"
            
        return toc
    
    def find_section(self, search_term: str) -> List[Dict]:
        """Find sections containing the search term"""
        results = []
        search_lower = search_term.lower()
        
        for section in self.sections:
            # Check section title
            if search_lower in section['title'].lower():
                results.append({
                    'type': 'section',
                    'title': section['title'],
                    'preview': ' '.join(section['content'][:3])
                })
            
            # Check subsections
            for subsection in section.get('subsections', []):
                if search_lower in subsection['title'].lower():
                    results.append({
                        'type': 'subsection',
                        'parent': section['title'],
                        'title': subsection['title'],
                        'preview': ' '.join(subsection['content'][:3])
                    })
                
                # Check content
                for line in subsection['content']:
                    if search_lower in line.lower():
                        results.append({
                            'type': 'content',
                            'parent': f"{section['title']} > {subsection['title']}",
                            'line': line,
                            'context': subsection['title']
                        })
                        
        return results
    
    def get_statistics(self) -> Dict:
        """Get comprehensive document statistics"""
        # Word frequency
        words = re.findall(r'\b\w+\b', self.content.lower())
        word_freq = Counter(words)
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be'}
        filtered_words = {w: c for w, c in word_freq.items() if w not in common_words and len(w) > 3}
        
        return {
            'total_sections': len(self.sections),
            'total_subsections': sum(len(s.get('subsections', [])) for s in self.sections),
            'total_words': len(words),
            'unique_words': len(set(words)),
            'average_words_per_line': len(words) / len([l for l in self.lines if l.strip()]),
            'most_common_terms': Counter(filtered_words).most_common(20),
            'section_sizes': [(s['title'], len(' '.join(s['content']).split())) for s in self.sections]
        }
    
    def suggest_improvements(self) -> List[str]:
        """Analyze document and suggest improvements"""
        suggestions = []
        
        # Check for very long sections
        for section in self.sections:
            content = ' '.join(section['content'])
            if len(content.split()) > 500:
                suggestions.append(f"Section '{section['title']}' is quite long ({len(content.split())} words). Consider breaking it into smaller subsections.")
        
        # Check for missing subsections
        for section in self.sections:
            if len(section.get('subsections', [])) == 0 and len(section['content']) > 10:
                suggestions.append(f"Section '{section['title']}' has no subsections but contains substantial content. Consider organizing with subsections.")
        
        # Check for consistency in formatting
        phone_patterns = [r'\d{3}-\d{3}-\d{4}', r'\(\d{3}\)\s*\d{3}-\d{4}', r'\d{3}\.\d{3}\.\d{4}']
        phone_formats = []
        for pattern in phone_patterns:
            if re.search(pattern, self.content):
                phone_formats.append(pattern)
        
        if len(phone_formats) > 1:
            suggestions.append("Multiple phone number formats detected. Consider standardizing to one format.")
        
        # Check for email consistency
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', self.content)
        if emails:
            domains = [e.split('@')[1].lower() for e in emails]
            if len(set(domains)) > 1:
                suggestions.append(f"Multiple email domains found: {set(domains)}. Verify all are correct.")
        
        return suggestions
    
    def export_structured(self, output_file='bmpoa_structured.json'):
        """Export document in structured format"""
        structured = {
            'title': 'Blue Mountain Property Owners Association Guide',
            'statistics': self.get_statistics(),
            'sections': self.sections,
            'suggestions': self.suggest_improvements()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured, f, indent=2)
            
        return output_file

def main():
    print("BMPOA Document Analysis and Editing Assistant")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = BMPOADocumentAnalyzer()
    
    # Display statistics
    stats = analyzer.get_statistics()
    print(f"\nDocument Statistics:")
    print(f"- Total sections: {stats['total_sections']}")
    print(f"- Total subsections: {stats['total_subsections']}")
    print(f"- Total words: {stats['total_words']}")
    print(f"- Unique words: {stats['unique_words']}")
    print(f"- Average words per line: {stats['average_words_per_line']:.1f}")
    
    print(f"\nMost common terms:")
    for term, count in stats['most_common_terms'][:10]:
        print(f"  - {term}: {count} times")
    
    # Show suggestions
    suggestions = analyzer.suggest_improvements()
    if suggestions:
        print(f"\nImprovement Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
    
    # Export structured version
    output_file = analyzer.export_structured()
    print(f"\nStructured document exported to: {output_file}")
    
    # Interactive search
    print("\nInteractive Search (type 'quit' to exit)")
    while True:
        search_term = input("\nSearch for: ").strip()
        if search_term.lower() == 'quit':
            break
            
        results = analyzer.find_section(search_term)
        if results:
            print(f"\nFound {len(results)} matches:")
            for i, result in enumerate(results[:10], 1):
                if result['type'] == 'section':
                    print(f"\n{i}. SECTION: {result['title']}")
                    print(f"   Preview: {result['preview'][:100]}...")
                elif result['type'] == 'subsection':
                    print(f"\n{i}. SUBSECTION: {result['title']} (in {result['parent']})")
                    print(f"   Preview: {result['preview'][:100]}...")
                else:
                    print(f"\n{i}. CONTENT: in {result['parent']}")
                    print(f"   Line: {result['line'][:100]}...")
        else:
            print("No matches found.")

if __name__ == "__main__":
    main()