#!/usr/bin/env python3
"""
BMPOA Document Image Auto-Reorganizer
Automatically reorganizes and resizes images in the document
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constants
DOCUMENT_ID = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
SERVICE_ACCOUNT_KEY = "service-account-key.json"
SCOPES = ['https://www.googleapis.com/auth/documents']

def main():
    print("=" * 60)
    print("BMPOA Document Image Auto-Reorganizer")
    print("=" * 60)
    
    # Authenticate
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_KEY,
            scopes=SCOPES
        )
        service = build('docs', 'v1', credentials=credentials)
        print("✅ Successfully authenticated!")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # Get document
    try:
        document = service.documents().get(documentId=DOCUMENT_ID).execute()
        print("✅ Document loaded successfully")
    except HttpError as e:
        print(f"❌ Error loading document: {e}")
        return
    
    # Find all inline objects (images)
    inline_objects = document.get('inlineObjects', {})
    print(f"\n📸 Found {len(inline_objects)} images to process")
    
    if not inline_objects:
        print("No images found in document")
        return
    
    # Create batch update requests
    requests = []
    max_width = 400  # Maximum width in points
    
    for obj_id, obj in inline_objects.items():
        props = obj.get('inlineObjectProperties', {})
        embedded = props.get('embeddedObject', {})
        
        # Get current size
        size = embedded.get('size', {})
        current_width = size.get('width', {}).get('magnitude', 0)
        current_height = size.get('height', {}).get('magnitude', 0)
        
        if current_width == 0 or current_height == 0:
            continue
        
        # Calculate aspect ratio
        aspect_ratio = current_width / current_height
        
        # Calculate new dimensions
        if current_width > max_width:
            new_width = max_width
            new_height = new_width / aspect_ratio
        else:
            new_width = current_width
            new_height = current_height
        
        print(f"\n   Image ID: {obj_id}")
        print(f"   Current: {current_width:.0f}x{current_height:.0f} PT")
        print(f"   New: {new_width:.0f}x{new_height:.0f} PT")
        
        # Create update request
        # First, update the embedded object position for better layout
        position_request = {
            'updateEmbeddedObjectPosition': {
                'objectId': obj_id,
                'newPosition': {
                    'layout': 'WRAP_TEXT',  # Allow text to wrap around image
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
                'fields': 'layout,size'
            }
        }
        
        requests.append(position_request)
    
    # Apply updates
    if requests:
        print(f"\n📝 Applying {len(requests)} image updates...")
        
        try:
            # Apply in chunks to avoid API limits
            chunk_size = 20
            total_chunks = (len(requests) + chunk_size - 1) // chunk_size
            
            for i in range(0, len(requests), chunk_size):
                chunk = requests[i:i + chunk_size]
                chunk_num = (i // chunk_size) + 1
                
                print(f"   Processing batch {chunk_num}/{total_chunks}...")
                
                result = service.documents().batchUpdate(
                    documentId=DOCUMENT_ID,
                    body={'requests': chunk}
                ).execute()
                
                print(f"   ✅ Batch {chunk_num} complete")
            
            print("\n✨ Successfully reorganized all images!")
            print(f"\n📄 View the updated document:")
            print(f"   https://docs.google.com/document/d/{DOCUMENT_ID}")
            
            # Generate summary
            print("\n📊 Summary:")
            print(f"   - Total images processed: {len(inline_objects)}")
            print(f"   - Images resized: {len([r for r in requests if 'updateEmbeddedObjectPosition' in r])}")
            print(f"   - Maximum width applied: {max_width} PT")
            
        except HttpError as e:
            print(f"\n❌ Error applying updates: {e}")
            if 'Invalid requests' in str(e):
                print("\nNote: Some images may be in tables or have special formatting.")
                print("These require manual adjustment.")
    else:
        print("\n✅ No image updates needed")

if __name__ == "__main__":
    main()