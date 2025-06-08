#!/usr/bin/env python3
"""
BMPOA Document Image Resizer
Resizes images by extracting and re-inserting them with new dimensions
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constants
DOCUMENT_ID = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
SERVICE_ACCOUNT_KEY = "service-account-key.json"
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

def main():
    print("=" * 60)
    print("BMPOA Document Image Resizer")
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
    
    # Analyze document structure
    content = document.get('body', {}).get('content', [])
    inline_objects = document.get('inlineObjects', {})
    
    print(f"\n📸 Found {len(inline_objects)} images in document")
    
    if not inline_objects:
        print("No images found")
        return
    
    # Find images that need resizing
    images_to_resize = []
    max_width = 400  # Maximum width in points
    
    for element in content:
        if 'paragraph' in element:
            paragraph = element['paragraph']
            for elem in paragraph.get('elements', []):
                if 'inlineObjectElement' in elem:
                    obj_id = elem['inlineObjectElement']['inlineObjectId']
                    start_index = elem.get('startIndex', 0)
                    end_index = elem.get('endIndex', 0)
                    
                    if obj_id in inline_objects:
                        obj = inline_objects[obj_id]
                        props = obj.get('inlineObjectProperties', {})
                        embedded = props.get('embeddedObject', {})
                        
                        # Get current size
                        size = embedded.get('size', {})
                        width = size.get('width', {}).get('magnitude', 0)
                        height = size.get('height', {}).get('magnitude', 0)
                        
                        # Get image URL
                        image_props = embedded.get('imageProperties', {})
                        content_uri = image_props.get('contentUri', '')
                        
                        if width > max_width:
                            # Calculate new dimensions
                            aspect_ratio = width / height if height > 0 else 1
                            new_width = max_width
                            new_height = new_width / aspect_ratio
                            
                            images_to_resize.append({
                                'object_id': obj_id,
                                'start_index': start_index,
                                'end_index': end_index,
                                'current_width': width,
                                'current_height': height,
                                'new_width': new_width,
                                'new_height': new_height,
                                'content_uri': content_uri,
                                'title': embedded.get('title', 'Untitled'),
                                'description': embedded.get('description', '')
                            })
    
    print(f"\n🔍 Found {len(images_to_resize)} images that need resizing (width > {max_width}pt)")
    
    if not images_to_resize:
        print("✅ All images are already properly sized")
        return
    
    # Sort images by index (reverse order to maintain positions)
    images_to_resize.sort(key=lambda x: x['start_index'], reverse=True)
    
    # Create batch requests
    requests = []
    
    for img in images_to_resize:
        print(f"\n📸 Processing: {img['title']}")
        print(f"   Current: {img['current_width']:.0f}x{img['current_height']:.0f}")
        print(f"   New: {img['new_width']:.0f}x{img['new_height']:.0f}")
        
        # Note: The Google Docs API doesn't support direct image resizing
        # We would need to:
        # 1. Delete the existing image
        # 2. Re-insert it with new dimensions
        # However, this requires the image to be accessible via URL
        
        # For now, we'll document what needs to be done
        print(f"   ⚠️  Image at index {img['start_index']} needs manual resizing")
    
    # Generate report
    print("\n" + "=" * 60)
    print("📊 RESIZE SUMMARY")
    print("=" * 60)
    
    print(f"\nTotal images: {len(inline_objects)}")
    print(f"Images needing resize: {len(images_to_resize)}")
    print(f"Maximum width setting: {max_width} PT")
    
    print("\n📝 Manual Resize Instructions:")
    print("Since the Google Docs API doesn't support direct image resizing,")
    print("please manually resize these images in the Google Docs editor:")
    
    for i, img in enumerate(images_to_resize, 1):
        print(f"\n{i}. {img['title']}")
        print(f"   Location: Character position {img['start_index']}")
        print(f"   Resize to: {img['new_width']:.0f}x{img['new_height']:.0f} PT")
        print(f"   (Maintain aspect ratio)")
    
    print(f"\n📄 Document URL:")
    print(f"   https://docs.google.com/document/d/{DOCUMENT_ID}")
    
    # Alternative: Use Google Apps Script
    print("\n💡 Alternative Solution:")
    print("You can use Google Apps Script to resize images:")
    print("1. Open the document")
    print("2. Extensions → Apps Script")
    print("3. Use the following code:")
    
    apps_script = '''
function resizeAllImages() {
  var doc = DocumentApp.openById('%s');
  var body = doc.getBody();
  var images = body.getImages();
  
  Logger.log('Found ' + images.length + ' images');
  
  images.forEach(function(image, index) {
    var width = image.getWidth();
    var height = image.getHeight();
    
    if (width > 400) {
      var ratio = 400 / width;
      var newHeight = height * ratio;
      
      image.setWidth(400);
      image.setHeight(newHeight);
      
      Logger.log('Resized image ' + (index + 1) + ': ' + width + 'x' + height + ' → 400x' + newHeight);
    }
  });
  
  doc.saveAndClose();
}
''' % DOCUMENT_ID
    
    with open('resize_images_script.gs', 'w') as f:
        f.write(apps_script)
    
    print("\n✅ Google Apps Script saved to: resize_images_script.gs")
    print("   Copy and paste this into the Apps Script editor and run it.")

if __name__ == "__main__":
    main()