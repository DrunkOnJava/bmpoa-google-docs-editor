#!/usr/bin/env python3
"""
BMPOA Document Duplicate Image Remover
Identifies and helps remove duplicate images from the document
"""

import os
import hashlib
from collections import defaultdict
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constants
DOCUMENT_ID = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
SERVICE_ACCOUNT_KEY = "service-account-key.json"
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive.readonly']

def main():
    print("=" * 60)
    print("BMPOA DOCUMENT DUPLICATE IMAGE FINDER")
    print("=" * 60)
    
    # Authenticate
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_KEY,
            scopes=SCOPES
        )
        docs_service = build('docs', 'v1', credentials=credentials)
        drive_service = build('drive', 'v3', credentials=credentials)
        print("✅ Successfully authenticated!")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # Get document
    try:
        document = docs_service.documents().get(documentId=DOCUMENT_ID).execute()
        print("✅ Document loaded successfully")
    except HttpError as e:
        print(f"❌ Error loading document: {e}")
        return
    
    # Get all inline objects
    inline_objects = document.get('inlineObjects', {})
    content = document.get('body', {}).get('content', [])
    
    print(f"\n📸 Analyzing {len(inline_objects)} images for duplicates...")
    
    # Build image information
    image_info = []
    image_positions = {}  # Map object ID to position in document
    
    # Find positions of images in document
    for element in content:
        if 'paragraph' in element:
            paragraph = element['paragraph']
            for elem in paragraph.get('elements', []):
                if 'inlineObjectElement' in elem:
                    obj_id = elem['inlineObjectElement']['inlineObjectId']
                    image_positions[obj_id] = {
                        'start_index': elem.get('startIndex', 0),
                        'end_index': elem.get('endIndex', 0)
                    }
    
    # Analyze each image
    for obj_id, obj in inline_objects.items():
        props = obj.get('inlineObjectProperties', {})
        embedded = props.get('embeddedObject', {})
        
        # Get image properties
        size = embedded.get('size', {})
        width = size.get('width', {}).get('magnitude', 0)
        height = size.get('height', {}).get('magnitude', 0)
        
        # Get image content URI
        image_props = embedded.get('imageProperties', {})
        content_uri = image_props.get('contentUri', '')
        source_uri = image_props.get('sourceUri', content_uri)
        
        # Create a fingerprint for the image
        fingerprint_data = f"{width}x{height}_{source_uri}"
        fingerprint = hashlib.md5(fingerprint_data.encode()).hexdigest()[:8]
        
        position = image_positions.get(obj_id, {})
        
        image_info.append({
            'id': obj_id,
            'title': embedded.get('title', 'Untitled'),
            'description': embedded.get('description', ''),
            'width': width,
            'height': height,
            'size_str': f"{width:.0f}x{height:.0f}",
            'content_uri': content_uri,
            'source_uri': source_uri,
            'fingerprint': fingerprint,
            'start_index': position.get('start_index', 0),
            'end_index': position.get('end_index', 0)
        })
    
    # Group by fingerprint to find duplicates
    duplicates = defaultdict(list)
    for img in image_info:
        duplicates[img['fingerprint']].append(img)
    
    # Find actual duplicates (more than one image with same fingerprint)
    duplicate_groups = {k: v for k, v in duplicates.items() if len(v) > 1}
    
    # Also check for same size images that might be duplicates
    size_groups = defaultdict(list)
    for img in image_info:
        size_groups[img['size_str']].append(img)
    
    potential_duplicates = {k: v for k, v in size_groups.items() if len(v) > 1}
    
    # Report findings
    print(f"\n📊 Duplicate Analysis Results:")
    print(f"   Total images: {len(image_info)}")
    print(f"   Confirmed duplicate groups: {len(duplicate_groups)}")
    print(f"   Same-size image groups: {len(potential_duplicates)}")
    
    if duplicate_groups:
        print(f"\n🔴 Confirmed Duplicates:")
        total_duplicates = 0
        for fingerprint, imgs in duplicate_groups.items():
            print(f"\n   Duplicate Group (fingerprint: {fingerprint}):")
            print(f"   Size: {imgs[0]['size_str']}")
            print(f"   Instances: {len(imgs)}")
            for i, img in enumerate(imgs):
                print(f"     {i+1}. Position: {img['start_index']}")
                print(f"        Title: {img['title']}")
                if img['description']:
                    print(f"        Description: {img['description']}")
            total_duplicates += len(imgs) - 1  # Count extras only
        
        print(f"\n   💡 Total duplicate images that could be removed: {total_duplicates}")
    
    if potential_duplicates and not duplicate_groups:
        print(f"\n🟡 Images with Same Dimensions (potential duplicates):")
        for size, imgs in potential_duplicates.items():
            if len(imgs) > 2:  # Only show if 3+ images of same size
                print(f"\n   Size: {size}")
                print(f"   Count: {len(imgs)}")
                for img in imgs[:5]:  # Show first 5
                    print(f"     - Position: {img['start_index']}, Title: {img['title']}")
    
    # Generate removal script
    if duplicate_groups:
        print(f"\n📝 Generating removal requests...")
        
        # Create requests to remove duplicates (keep first instance)
        removal_requests = []
        for fingerprint, imgs in duplicate_groups.items():
            # Sort by position to keep the first occurrence
            imgs.sort(key=lambda x: x['start_index'])
            
            # Remove all but the first
            for img in imgs[1:]:
                removal_requests.append({
                    'deleteContentRange': {
                        'range': {
                            'startIndex': img['start_index'],
                            'endIndex': img['end_index']
                        }
                    }
                })
        
        # Sort requests in reverse order to maintain indices
        removal_requests.sort(key=lambda x: x['deleteContentRange']['range']['startIndex'], reverse=True)
        
        print(f"\n⚠️  Found {len(removal_requests)} duplicate images to remove")
        
        # Save removal script
        script = f'''
# Duplicate Image Removal Script for BMPOA Document
# Generated requests to remove {len(removal_requests)} duplicate images

import json

# Document ID
DOCUMENT_ID = "{DOCUMENT_ID}"

# Removal requests (in reverse order to maintain indices)
removal_requests = {json.dumps(removal_requests, indent=2)}

# To apply these removals:
# 1. Use the Google Docs API batchUpdate method
# 2. Send these requests in the order provided
# 3. The duplicates will be removed while keeping the first instance

print(f"Ready to remove {{len(removal_requests)}} duplicate images")
'''
        
        with open('remove_duplicates_requests.py', 'w') as f:
            f.write(script)
        
        print(f"✅ Removal script saved to: remove_duplicates_requests.py")
        
        # Create Apps Script version
        apps_script = '''
function removeDuplicateImages() {
  var doc = DocumentApp.openById('%s');
  var body = doc.getBody();
  
  // Get all images
  var images = body.getImages();
  var imageMap = {};
  var duplicates = [];
  
  Logger.log('Checking ' + images.length + ' images for duplicates...');
  
  // Create fingerprint for each image
  images.forEach(function(image, index) {
    var width = image.getWidth();
    var height = image.getHeight();
    var altText = image.getAltDescription() || '';
    var altTitle = image.getAltTitle() || '';
    
    // Create a fingerprint
    var fingerprint = width + 'x' + height + '_' + altText + '_' + altTitle;
    
    if (imageMap[fingerprint]) {
      // Found a duplicate
      duplicates.push({
        index: index,
        image: image,
        fingerprint: fingerprint
      });
    } else {
      // First occurrence
      imageMap[fingerprint] = {
        index: index,
        image: image
      };
    }
  });
  
  Logger.log('Found ' + duplicates.length + ' duplicate images');
  
  // Remove duplicates (in reverse order to maintain indices)
  duplicates.reverse().forEach(function(dup) {
    try {
      dup.image.removeFromParent();
      Logger.log('Removed duplicate image at index ' + dup.index);
    } catch (e) {
      Logger.log('Error removing image at index ' + dup.index + ': ' + e);
    }
  });
  
  // Save document
  doc.saveAndClose();
  
  // Show summary
  var ui = DocumentApp.getUi();
  ui.alert('Duplicate Removal Complete', 
           'Removed ' + duplicates.length + ' duplicate images from the document.', 
           ui.ButtonSet.OK);
}
''' % DOCUMENT_ID
        
        with open('remove_duplicates.gs', 'w') as f:
            f.write(apps_script)
        
        print(f"✅ Apps Script saved to: remove_duplicates.gs")
        print(f"\n📋 To remove duplicates:")
        print(f"   1. Open document: https://docs.google.com/document/d/{DOCUMENT_ID}")
        print(f"   2. Extensions → Apps Script")
        print(f"   3. Paste content from remove_duplicates.gs")
        print(f"   4. Run removeDuplicateImages() function")
    
    else:
        print(f"\n✅ No confirmed duplicate images found!")
    
    # Summary
    print(f"\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total images analyzed: {len(image_info)}")
    print(f"Unique images: {len(image_info) - sum(len(imgs) - 1 for imgs in duplicate_groups.values())}")
    print(f"Duplicate images found: {sum(len(imgs) - 1 for imgs in duplicate_groups.values())}")

if __name__ == "__main__":
    main()