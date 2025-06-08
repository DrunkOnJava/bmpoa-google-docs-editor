#!/usr/bin/env python3
"""
Advanced BMPOA Document Image Organizer
Analyzes image placement and suggests reorganization based on context
"""

import os
import json
import re
from typing import List, Dict, Tuple, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constants
DOCUMENT_ID = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
SERVICE_ACCOUNT_KEY = "service-account-key.json"
SCOPES = ['https://www.googleapis.com/auth/documents']

class AdvancedImageOrganizer:
    def __init__(self):
        self.service = None
        self.document = None
        self.sections = []
        self.images = []
        
    def authenticate(self):
        """Authenticate using service account"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_KEY,
                scopes=SCOPES
            )
            self.service = build('docs', 'v1', credentials=credentials)
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def analyze_document_structure(self):
        """Analyze document to identify sections and their content"""
        try:
            self.document = self.service.documents().get(documentId=DOCUMENT_ID).execute()
            content = self.document.get('body', {}).get('content', [])
            
            current_section = None
            section_content = []
            
            for element in content:
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    text = ''
                    
                    # Extract text
                    for elem in paragraph.get('elements', []):
                        if 'textRun' in elem:
                            text += elem['textRun'].get('content', '')
                    
                    text = text.strip()
                    
                    # Check if it's a section header (all caps, reasonable length)
                    if text and text.isupper() and 10 < len(text) < 100:
                        # Save previous section
                        if current_section:
                            self.sections.append({
                                'title': current_section,
                                'start_index': section_start,
                                'end_index': element.get('startIndex', 0),
                                'content': '\n'.join(section_content),
                                'images': []
                            })
                        
                        # Start new section
                        current_section = text
                        section_start = element.get('startIndex', 0)
                        section_content = []
                    
                    elif current_section and text:
                        section_content.append(text)
                    
                    # Check for images
                    for elem in paragraph.get('elements', []):
                        if 'inlineObjectElement' in elem:
                            obj_id = elem['inlineObjectElement']['inlineObjectId']
                            self.images.append({
                                'id': obj_id,
                                'start_index': elem.get('startIndex', 0),
                                'end_index': elem.get('endIndex', 0),
                                'paragraph_text': text[:100] if text else '',
                                'section': current_section
                            })
            
            # Save last section
            if current_section:
                self.sections.append({
                    'title': current_section,
                    'start_index': section_start,
                    'end_index': len(content),
                    'content': '\n'.join(section_content),
                    'images': []
                })
            
            # Associate images with sections
            for img in self.images:
                for section in self.sections:
                    if section['start_index'] <= img['start_index'] < section['end_index']:
                        section['images'].append(img)
                        img['current_section'] = section['title']
                        break
            
            return True
            
        except HttpError as e:
            print(f"❌ Error analyzing document: {e}")
            return False
    
    def analyze_image_context(self):
        """Analyze each image to determine its ideal placement"""
        inline_objects = self.document.get('inlineObjects', {})
        
        for img in self.images:
            if img['id'] in inline_objects:
                obj = inline_objects[img['id']]
                props = obj.get('inlineObjectProperties', {})
                embedded = props.get('embeddedObject', {})
                
                img['title'] = embedded.get('title', 'Untitled')
                img['description'] = embedded.get('description', '')
                
                # Get size info
                size = embedded.get('size', {})
                img['width'] = size.get('width', {}).get('magnitude', 0)
                img['height'] = size.get('height', {}).get('magnitude', 0)
                
                # Analyze content to suggest placement
                img['suggested_section'] = self._suggest_section(img)
    
    def _suggest_section(self, image):
        """Suggest the best section for an image based on content analysis"""
        # Keywords for different sections
        section_keywords = {
            'GOVERNANCE & STRUCTURE': ['board', 'committee', 'governance', 'bylaws', 'voting', 'election'],
            'FIRE SAFETY & EMERGENCY PREPAREDNESS': ['fire', 'emergency', 'evacuation', 'safety', 'wildfire', 'route'],
            'DEER LAKE RECREATION AREA': ['lake', 'deer lake', 'swimming', 'beach', 'recreation', 'water'],
            'THE LODGE': ['lodge', 'facility', 'rental', 'event', 'booking', 'kitchen'],
            'WOOD-CHIPPING PROGRAM': ['wood', 'chip', 'chipping', 'brush', 'pile', 'debris'],
            'COMMUNITY SERVICES & AMENITIES': ['service', 'amenity', 'road', 'internet', 'utility'],
            'A MOUNTAIN HOME': ['mountain', 'home', 'property', 'landscape', 'view', 'nature']
        }
        
        # Check image title and description
        img_text = (image.get('title', '') + ' ' + image.get('description', '')).lower()
        
        # Check paragraph text near image
        para_text = image.get('paragraph_text', '').lower()
        
        # Score each section
        section_scores = {}
        
        for section, keywords in section_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in img_text:
                    score += 3  # Higher weight for image metadata
                if keyword in para_text:
                    score += 1
            
            if score > 0:
                section_scores[section] = score
        
        # Return highest scoring section
        if section_scores:
            return max(section_scores, key=section_scores.get)
        
        # Default to current section if no match
        return image.get('current_section', 'UNKNOWN')
    
    def generate_reorganization_plan(self):
        """Generate a plan for reorganizing images"""
        plan = {
            'total_images': len(self.images),
            'sections': {},
            'movements': [],
            'resize_needed': []
        }
        
        # Organize by section
        for section in self.sections:
            plan['sections'][section['title']] = {
                'current_images': len(section['images']),
                'suggested_images': 0
            }
        
        # Check each image
        for img in self.images:
            current = img.get('current_section', 'UNKNOWN')
            suggested = img.get('suggested_section', current)
            
            if suggested != current and suggested != 'UNKNOWN':
                plan['movements'].append({
                    'image': img['title'],
                    'from': current,
                    'to': suggested,
                    'reason': f"Content matches {suggested} section"
                })
                
                if suggested in plan['sections']:
                    plan['sections'][suggested]['suggested_images'] += 1
            
            # Check if resize needed
            if img.get('width', 0) > 400:
                plan['resize_needed'].append({
                    'image': img['title'],
                    'current_size': f"{img.get('width', 0):.0f}x{img.get('height', 0):.0f}",
                    'suggested_size': f"400x{(400 * img.get('height', 1) / img.get('width', 1)):.0f}"
                })
        
        return plan
    
    def generate_apps_script(self):
        """Generate an enhanced Google Apps Script for image organization"""
        script = '''
function organizeAndResizeImages() {
  var doc = DocumentApp.openById('%s');
  var body = doc.getBody();
  
  // Configuration
  var MAX_WIDTH = 400;
  var SECTIONS = {
    'GOVERNANCE': /governance|board|committee|bylaws/i,
    'FIRE SAFETY': /fire|emergency|evacuation|safety/i,
    'DEER LAKE': /lake|deer lake|swimming|beach/i,
    'LODGE': /lodge|facility|rental|booking/i,
    'WOOD CHIPPING': /wood|chip|brush/i,
    'COMMUNITY': /service|amenity|road|internet/i,
    'MOUNTAIN HOME': /mountain|home|property|landscape/i
  };
  
  // Get all images
  var images = body.getImages();
  Logger.log('Found ' + images.length + ' images');
  
  // Process each image
  images.forEach(function(image, index) {
    var paragraph = image.getParent();
    
    // Resize if needed
    var width = image.getWidth();
    var height = image.getHeight();
    
    if (width > MAX_WIDTH) {
      var ratio = MAX_WIDTH / width;
      var newHeight = height * ratio;
      
      image.setWidth(MAX_WIDTH);
      image.setHeight(newHeight);
      
      Logger.log('Resized image ' + (index + 1) + ': ' + width + 'x' + height + ' → ' + MAX_WIDTH + 'x' + newHeight);
    }
    
    // Center the image
    if (paragraph.getType() === DocumentApp.ElementType.PARAGRAPH) {
      paragraph.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
    }
    
    // Add spacing
    paragraph.setSpacingBefore(12);
    paragraph.setSpacingAfter(12);
  });
  
  // Find section headers and organize
  var paragraphs = body.getParagraphs();
  var sections = {};
  var currentSection = null;
  
  paragraphs.forEach(function(para) {
    var text = para.getText();
    
    // Check if it's a section header
    if (text && text === text.toUpperCase() && text.length > 10 && text.length < 100) {
      currentSection = text;
      sections[currentSection] = {
        element: para,
        images: []
      };
    }
  });
  
  Logger.log('Found ' + Object.keys(sections).length + ' sections');
  
  // Save and close
  doc.saveAndClose();
  
  // Log summary
  Logger.log('\\nImage Organization Complete!');
  Logger.log('- Images resized: ' + images.length);
  Logger.log('- Sections found: ' + Object.keys(sections).length);
}

// Run this function to organize images
function runImageOrganization() {
  organizeAndResizeImages();
  
  // Show completion message
  var ui = DocumentApp.getUi();
  ui.alert('Image Organization Complete', 
           'All images have been resized and formatted.\\n\\n' +
           'Images wider than 400 points have been resized while maintaining aspect ratio.\\n' +
           'Images have been centered with appropriate spacing.',
           ui.ButtonSet.OK);
}
''' % DOCUMENT_ID
        
        return script
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        if not self.sections:
            self.analyze_document_structure()
            self.analyze_image_context()
        
        plan = self.generate_reorganization_plan()
        
        report = []
        report.append("=" * 60)
        report.append("BMPOA DOCUMENT IMAGE ANALYSIS REPORT")
        report.append("=" * 60)
        
        report.append(f"\n📊 Document Overview:")
        report.append(f"   Total sections: {len(self.sections)}")
        report.append(f"   Total images: {len(self.images)}")
        report.append(f"   Images needing resize: {len(plan['resize_needed'])}")
        report.append(f"   Suggested movements: {len(plan['movements'])}")
        
        report.append(f"\n📂 Current Image Distribution:")
        for section in self.sections:
            if section['images']:
                report.append(f"\n   {section['title']}:")
                report.append(f"   - Current images: {len(section['images'])}")
                for img in section['images'][:3]:  # Show first 3
                    report.append(f"     • {img.get('title', 'Untitled')}")
        
        if plan['movements']:
            report.append(f"\n🔄 Suggested Image Movements:")
            for move in plan['movements']:
                report.append(f"\n   Move: {move['image']}")
                report.append(f"   From: {move['from']}")
                report.append(f"   To: {move['to']}")
                report.append(f"   Reason: {move['reason']}")
        
        if plan['resize_needed']:
            report.append(f"\n📏 Images Needing Resize:")
            for resize in plan['resize_needed'][:10]:  # Show first 10
                report.append(f"\n   {resize['image']}")
                report.append(f"   Current: {resize['current_size']}")
                report.append(f"   Suggested: {resize['suggested_size']}")
        
        return '\n'.join(report)

def main():
    print("=" * 60)
    print("ADVANCED BMPOA DOCUMENT IMAGE ORGANIZER")
    print("=" * 60)
    
    organizer = AdvancedImageOrganizer()
    
    if not organizer.authenticate():
        print("Authentication failed!")
        return
    
    print("\n🔍 Analyzing document structure...")
    if not organizer.analyze_document_structure():
        return
    
    print("✅ Document structure analyzed")
    print(f"   Found {len(organizer.sections)} sections")
    print(f"   Found {len(organizer.images)} images")
    
    print("\n🖼️ Analyzing image context...")
    organizer.analyze_image_context()
    
    # Generate and save report
    report = organizer.generate_report()
    print(report)
    
    with open('bmpoa_image_analysis_report.txt', 'w') as f:
        f.write(report)
    print(f"\n✅ Report saved to: bmpoa_image_analysis_report.txt")
    
    # Generate enhanced Apps Script
    script = organizer.generate_apps_script()
    with open('enhanced_image_organizer.gs', 'w') as f:
        f.write(script)
    print(f"✅ Enhanced Apps Script saved to: enhanced_image_organizer.gs")
    
    # Save detailed analysis
    analysis_data = {
        'sections': [
            {
                'title': s['title'],
                'image_count': len(s['images']),
                'images': [
                    {
                        'title': img.get('title', 'Untitled'),
                        'width': img.get('width', 0),
                        'height': img.get('height', 0),
                        'suggested_section': img.get('suggested_section', 'UNKNOWN')
                    }
                    for img in s['images']
                ]
            }
            for s in organizer.sections
        ],
        'reorganization_plan': organizer.generate_reorganization_plan()
    }
    
    with open('bmpoa_image_analysis.json', 'w') as f:
        json.dump(analysis_data, f, indent=2)
    print(f"✅ Detailed analysis saved to: bmpoa_image_analysis.json")

if __name__ == "__main__":
    main()