#!/usr/bin/env python3
"""
Generate comprehensive report on BMPOA document with editing recommendations
"""

import json
import re
from datetime import datetime

def generate_report():
    # Load the structured data
    with open('bmpoa_structured.json', 'r') as f:
        data = json.load(f)
    
    # Load original content for specific analysis
    with open('bmpoa_document.txt', 'r') as f:
        content = f.read()
    
    report = []
    report.append("BMPOA DOCUMENT ANALYSIS REPORT")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Executive Summary
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 40)
    stats = data['statistics']
    report.append(f"The Blue Mountain Property Owners Association Guide contains {stats['total_words']} words")
    report.append(f"organized into {stats['total_sections']} main sections and {stats['total_subsections']} subsections.")
    report.append("")
    
    # Key Topics
    report.append("KEY TOPICS (by frequency):")
    for term, count in stats['most_common_terms'][:15]:
        report.append(f"  • {term.capitalize()}: {count} occurrences")
    report.append("")
    
    # Document Structure
    report.append("DOCUMENT STRUCTURE")
    report.append("-" * 40)
    for section in data['sections']:
        word_count = len(' '.join(section['content']).split())
        report.append(f"\n{section['title']} ({word_count} words)")
        for subsection in section.get('subsections', []):
            sub_words = len(' '.join(subsection['content']).split())
            report.append(f"    {subsection['title']} ({sub_words} words)")
    report.append("")
    
    # Contact Information Audit
    report.append("\nCONTACT INFORMATION AUDIT")
    report.append("-" * 40)
    
    # Find all phone numbers
    phone_patterns = [
        (r'\d{3}-\d{3}-\d{4}', 'XXX-XXX-XXXX'),
        (r'\(\d{3}\)\s*\d{3}-\d{4}', '(XXX) XXX-XXXX'),
        (r'\d{3}\.\d{3}\.\d{4}', 'XXX.XXX.XXXX')
    ]
    
    phones_found = []
    for pattern, format_name in phone_patterns:
        matches = re.findall(pattern, content)
        if matches:
            phones_found.append(f"  Format '{format_name}': {len(matches)} instances")
            for phone in set(matches):
                phones_found.append(f"    - {phone}")
    
    if phones_found:
        report.append("Phone Numbers Found:")
        report.extend(phones_found)
    
    # Find all emails
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
    if emails:
        report.append("\nEmail Addresses Found:")
        for email in sorted(set(emails)):
            report.append(f"  - {email}")
    
    # Find all URLs
    urls = re.findall(r'https?://[^\s]+', content)
    if urls:
        report.append("\nWebsites Found:")
        for url in sorted(set(urls)):
            report.append(f"  - {url}")
    report.append("")
    
    # Specific Content Analysis
    report.append("\nSPECIFIC CONTENT AREAS")
    report.append("-" * 40)
    
    # Emergency Information
    report.append("\n1. EMERGENCY & SAFETY INFORMATION")
    emergency_keywords = ['emergency', '911', 'evacuation', 'fire', 'safety']
    for keyword in emergency_keywords:
        count = len(re.findall(r'\b' + keyword + r'\b', content, re.IGNORECASE))
        if count > 0:
            report.append(f"   - '{keyword}' mentioned {count} times")
    
    # Governance
    report.append("\n2. GOVERNANCE STRUCTURE")
    governance_keywords = ['board', 'committee', 'meeting', 'vote', 'bylaws', 'covenant']
    for keyword in governance_keywords:
        count = len(re.findall(r'\b' + keyword + r'\b', content, re.IGNORECASE))
        if count > 0:
            report.append(f"   - '{keyword}' mentioned {count} times")
    
    # Amenities
    report.append("\n3. COMMUNITY AMENITIES")
    amenity_keywords = ['lodge', 'lake', 'trail', 'recreation', 'playground', 'pool']
    for keyword in amenity_keywords:
        count = len(re.findall(r'\b' + keyword + r'\b', content, re.IGNORECASE))
        if count > 0:
            report.append(f"   - '{keyword}' mentioned {count} times")
    
    # Recommendations
    report.append("\n\nEDITING RECOMMENDATIONS")
    report.append("-" * 40)
    
    # From automated suggestions
    if data.get('suggestions'):
        report.append("\nAutomated Suggestions:")
        for i, suggestion in enumerate(data['suggestions'], 1):
            report.append(f"{i}. {suggestion}")
    
    # Additional recommendations
    report.append("\nAdditional Editorial Recommendations:")
    
    # Check for date references
    current_year = datetime.now().year
    year_pattern = r'\b(19|20)\d{2}\b'
    years_found = re.findall(year_pattern, content)
    if years_found:
        old_years = [y for y in years_found if int(y) < current_year - 2]
        if old_years:
            report.append(f"1. Update outdated year references: {sorted(set(old_years))}")
    
    # Check section balance
    section_sizes = stats.get('section_sizes', [])
    if section_sizes:
        avg_size = sum(size for _, size in section_sizes) / len(section_sizes)
        unbalanced = [(name, size) for name, size in section_sizes if size > avg_size * 2 or size < avg_size * 0.3]
        if unbalanced:
            report.append("2. Consider rebalancing these sections:")
            for name, size in unbalanced:
                if size > avg_size * 2:
                    report.append(f"   - {name}: Too long ({size} words, avg is {avg_size:.0f})")
                else:
                    report.append(f"   - {name}: Too short ({size} words, avg is {avg_size:.0f})")
    
    # Accessibility
    report.append("\n3. Accessibility Improvements:")
    report.append("   - Add alt text descriptions for any images")
    report.append("   - Ensure all links have descriptive text")
    report.append("   - Consider adding a glossary for technical terms")
    
    # Save report
    report_text = '\n'.join(report)
    
    with open('bmpoa_document_report.txt', 'w') as f:
        f.write(report_text)
    
    print(report_text)
    print(f"\n\nFull report saved to: bmpoa_document_report.txt")
    
    # Create a summary for quick reference
    summary = {
        'document_title': 'Blue Mountain Property Owners Association Guide',
        'total_words': stats['total_words'],
        'sections': stats['total_sections'],
        'last_analyzed': datetime.now().isoformat(),
        'key_topics': dict(stats['most_common_terms'][:10]),
        'contacts': {
            'emails': sorted(set(emails)) if emails else [],
            'phones': list(set(re.findall(r'[\d\(\)\.\-\s]{10,}', content))),
            'websites': sorted(set(urls)) if urls else []
        },
        'recommendations_count': len(data.get('suggestions', [])) + 3
    }
    
    with open('bmpoa_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary data saved to: bmpoa_summary.json")

if __name__ == "__main__":
    generate_report()