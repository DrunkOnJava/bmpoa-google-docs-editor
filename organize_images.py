#!/usr/bin/env python3
"""
BMPOA Document Image Organizer
Finds, analyzes, and reorganizes images in the document
"""

import os
import json
from typing import List, Dict, Tuple, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constants
DOCUMENT_ID = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
SERVICE_ACCOUNT_KEY = "service-account-key.json"
SCOPES = ['https://www.googleapis.com/auth/documents']

class ImageOrganizer:
    def __init__(self):
        self.service = None
        self.document = None
        self.images = []
        self.paragraphs = []
        
    def authenticate(self):
        """Authenticate using service account"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_KEY,
                scopes=SCOPES
            )
            self.service = build('docs', 'v1', credentials=credentials)
            print("✅ Successfully authenticated!")
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def analyze_document(self):
        """Analyze document structure and find all images"""
        try:
            self.document = self.service.documents().get(documentId=DOCUMENT_ID).execute()
            content = self.document.get('body', {}).get('content', [])
            
            self.images = []
            self.paragraphs = []
            
            for i, element in enumerate(content):
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    para_info = {
                        'index': i,
                        'start_index': element.get('startIndex', 0),
                        'end_index': element.get('endIndex', 0),
                        'text': '',
                        'has_image': False,
                        'images': []
                    }
                    
                    # Check for images and text in paragraph elements
                    for elem in paragraph.get('elements', []):
                        if 'textRun' in elem:
                            para_info['text'] += elem['textRun'].get('content', '')
                        
                        elif 'inlineObjectElement' in elem:
                            inline_obj_id = elem['inlineObjectElement']['inlineObjectId']
                            inline_objects = self.document.get('inlineObjects', {})
                            
                            if inline_obj_id in inline_objects:
                                inline_obj = inline_objects[inline_obj_id]
                                embedded_obj = inline_obj.get('inlineObjectProperties', {}).get('embeddedObject', {})
                                
                                image_info = {
                                    'inline_object_id': inline_obj_id,
                                    'element_index': i,
                                    'start_index': elem.get('startIndex', 0),
                                    'end_index': elem.get('endIndex', 0),
                                    'paragraph_index': element.get('startIndex', 0),
                                    'title': embedded_obj.get('title', 'Untitled Image'),
                                    'description': embedded_obj.get('description', ''),
                                    'size': embedded_obj.get('size', {}),
                                    'properties': inline_obj.get('inlineObjectProperties', {}),
                                    'current_dimensions': self._get_current_dimensions(inline_obj),
                                    'aspect_ratio': self._calculate_aspect_ratio(embedded_obj.get('size', {}))
                                }
                                
                                self.images.append(image_info)
                                para_info['has_image'] = True
                                para_info['images'].append(image_info)
                    
                    # Store paragraph info
                    para_info['text'] = para_info['text'].strip()
                    self.paragraphs.append(para_info)
            
            print(f"\n📊 Document Analysis Complete:")
            print(f"   - Total paragraphs: {len(self.paragraphs)}")
            print(f"   - Total images: {len(self.images)}")
            
            return True
            
        except HttpError as e:
            print(f"❌ Error analyzing document: {e}")
            return False
    
    def _get_current_dimensions(self, inline_object):
        """Extract current image dimensions"""
        props = inline_object.get('inlineObjectProperties', {})
        embedded = props.get('embeddedObject', {})
        
        # Get original size
        size = embedded.get('size', {})
        width = size.get('width', {}).get('magnitude', 0)
        height = size.get('height', {}).get('magnitude', 0)
        
        return {
            'width': width,
            'height': height,
            'unit': size.get('width', {}).get('unit', 'PT')
        }
    
    def _calculate_aspect_ratio(self, size):
        """Calculate aspect ratio from size object"""
        width = size.get('width', {}).get('magnitude', 1)
        height = size.get('height', {}).get('magnitude', 1)
        
        if height > 0:
            return width / height
        return 1.0
    
    def find_image_context(self):
        """Find appropriate context for each image"""
        image_contexts = []
        
        for img in self.images:
            context = {
                'image': img,
                'current_paragraph': None,
                'nearby_text': '',
                'suggested_location': None,
                'reason': ''
            }
            
            # Find the paragraph containing this image
            for para in self.paragraphs:
                if para['start_index'] <= img['start_index'] < para['end_index']:
                    context['current_paragraph'] = para
                    break
            
            # Get surrounding text (5 paragraphs before and after)
            para_idx = next((i for i, p in enumerate(self.paragraphs) 
                            if p.get('start_index', 0) <= img['start_index'] < p.get('end_index', 0)), -1)
            
            if para_idx >= 0:
                start_idx = max(0, para_idx - 5)
                end_idx = min(len(self.paragraphs), para_idx + 6)
                
                nearby_texts = []
                for i in range(start_idx, end_idx):
                    if self.paragraphs[i]['text']:
                        nearby_texts.append(self.paragraphs[i]['text'])
                
                context['nearby_text'] = ' '.join(nearby_texts)
            
            # Analyze context to suggest placement
            context = self._suggest_image_placement(context)
            image_contexts.append(context)
        
        return image_contexts
    
    def _suggest_image_placement(self, context):
        """Suggest where image should be placed based on content"""
        nearby_text = context['nearby_text'].lower()
        img_title = context['image']['title'].lower()
        img_desc = context['image']['description'].lower()
        
        # Keywords that might indicate where image belongs
        section_keywords = {
            'fire': ['fire', 'evacuation', 'emergency', 'safety', 'wildfire'],
            'lodge': ['lodge', 'facility', 'rental', 'booking', 'event'],
            'lake': ['lake', 'deer lake', 'recreation', 'swimming', 'beach'],
            'map': ['map', 'location', 'boundary', 'property', 'area'],
            'landscape': ['mountain', 'view', 'scenery', 'landscape', 'nature'],
            'community': ['community', 'residents', 'neighborhood', 'activities'],
            'governance': ['board', 'committee', 'governance', 'meeting', 'election']
        }
        
        # Check image title/description and nearby text for keywords
        for section, keywords in section_keywords.items():
            for keyword in keywords:
                if keyword in img_title or keyword in img_desc or keyword in nearby_text:
                    context['suggested_location'] = section
                    context['reason'] = f"Image appears to be related to {section} based on keyword '{keyword}'"
                    return context
        
        # If no specific match, keep current location
        context['suggested_location'] = 'current'
        context['reason'] = 'No specific section match found, keeping current location'
        
        return context
    
    def create_image_update_requests(self, max_width: int = 400):
        """Create batch update requests to reorganize and resize images"""
        requests = []
        
        # First, analyze all images and their contexts
        image_contexts = self.find_image_context()
        
        for ctx in image_contexts:
            img = ctx['image']
            
            # Calculate new dimensions maintaining aspect ratio
            aspect_ratio = img['aspect_ratio']
            current_width = img['current_dimensions']['width']
            current_height = img['current_dimensions']['height']
            
            # Determine new size (max width while maintaining aspect ratio)
            if current_width > max_width:
                new_width = max_width
                new_height = new_width / aspect_ratio
            else:
                # Keep current size if already smaller than max
                new_width = current_width
                new_height = current_height
            
            # Create update request for image properties
            update_request = {
                'updateEmbeddedObjectPosition': {
                    'objectId': img['inline_object_id'],
                    'newPosition': {
                        'layout': 'WRAP_TEXT',
                        'leftOffset': {
                            'magnitude': 0,
                            'unit': 'PT'
                        },
                        'topOffset': {
                            'magnitude': 0,
                            'unit': 'PT'
                        }
                    },
                    'fields': 'layout,leftOffset,topOffset'
                }
            }
            
            # Add size update
            size_request = {
                'updateEmbeddedObjectPosition': {
                    'objectId': img['inline_object_id'],
                    'newPosition': {
                        'size': {
                            'width': {
                                'magnitude': new_width,
                                'unit': 'PT'
                            },
                            'height': {
                                'magnitude': new_height,
                                'unit': 'PT'
                            }
                        }
                    },
                    'fields': 'size'
                }
            }
            
            requests.extend([update_request, size_request])
            
            print(f"\n📸 Image: {img['title']}")
            print(f"   Current size: {current_width:.0f}x{current_height:.0f}")
            print(f"   New size: {new_width:.0f}x{new_height:.0f}")
            print(f"   Location: {ctx['reason']}")
        
        return requests
    
    def reorganize_images(self, max_width: int = 400, dry_run: bool = True):
        """Main function to reorganize all images"""
        print("\n🔍 Analyzing document structure...")
        if not self.analyze_document():
            return False
        
        if len(self.images) == 0:
            print("ℹ️  No images found in the document")
            return True
        
        print(f"\n🖼️  Found {len(self.images)} images to process")
        
        # Create update requests
        requests = self.create_image_update_requests(max_width)
        
        if dry_run:
            print(f"\n⚠️  DRY RUN: Would make {len(requests)} updates")
            print("Set dry_run=False to apply changes")
            return True
        
        # Apply updates in batches
        if requests:
            try:
                print(f"\n📝 Applying {len(requests)} updates...")
                
                # Google Docs API has a limit on batch size, so we'll chunk requests
                chunk_size = 50
                for i in range(0, len(requests), chunk_size):
                    chunk = requests[i:i + chunk_size]
                    
                    result = self.service.documents().batchUpdate(
                        documentId=DOCUMENT_ID,
                        body={'requests': chunk}
                    ).execute()
                    
                    print(f"   ✅ Applied batch {i//chunk_size + 1}/{(len(requests) + chunk_size - 1)//chunk_size}")
                
                print("\n✨ Successfully reorganized all images!")
                return True
                
            except HttpError as e:
                print(f"\n❌ Error applying updates: {e}")
                return False
        
        return True
    
    def generate_image_report(self):
        """Generate a report of all images and their status"""
        if not self.images:
            self.analyze_document()
        
        report = []
        report.append("BMPOA Document Image Report")
        report.append("=" * 60)
        report.append(f"\nTotal Images: {len(self.images)}")
        
        contexts = self.find_image_context()
        
        for i, ctx in enumerate(contexts, 1):
            img = ctx['image']
            report.append(f"\n{i}. {img['title']}")
            report.append(f"   Size: {img['current_dimensions']['width']:.0f}x{img['current_dimensions']['height']:.0f} PT")
            report.append(f"   Aspect Ratio: {img['aspect_ratio']:.2f}")
            report.append(f"   Location: Index {img['start_index']}")
            report.append(f"   Context: {ctx['reason']}")
            
            if img['description']:
                report.append(f"   Description: {img['description']}")
        
        report_text = '\n'.join(report)
        
        with open('bmpoa_images_report.txt', 'w') as f:
            f.write(report_text)
        
        print(report_text)
        print(f"\n✅ Report saved to bmpoa_images_report.txt")
        
        return report_text

def main():
    print("=" * 60)
    print("BMPOA Document Image Organizer")
    print("=" * 60)
    
    organizer = ImageOrganizer()
    
    if not organizer.authenticate():
        return
    
    # Generate image report first
    print("\n📊 Generating image analysis report...")
    organizer.generate_image_report()
    
    # Ask about reorganization
    print("\n" + "=" * 60)
    print("\nOptions:")
    print("1. Reorganize images (dry run)")
    print("2. Reorganize images (apply changes)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        print("\n🔄 Running image reorganization (DRY RUN)...")
        organizer.reorganize_images(max_width=400, dry_run=True)
    
    elif choice == '2':
        confirm = input("\n⚠️  This will modify the document. Continue? (yes/no): ").strip().lower()
        if confirm == 'yes':
            print("\n🔄 Reorganizing images...")
            organizer.reorganize_images(max_width=400, dry_run=False)
            print(f"\n✅ Done! View the document: https://docs.google.com/document/d/{DOCUMENT_ID}")
        else:
            print("Cancelled.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()