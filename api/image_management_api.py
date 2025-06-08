#!/usr/bin/env python3
"""
AGENT 1 - Image Management API
Endpoints for image organization and movement in Google Docs
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
sys.path.append('..')

from enhanced_gdocs_api import EnhancedGoogleDocsAPI
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

# Initialize API
api = EnhancedGoogleDocsAPI()
api.authenticate()

# Document sections mapping
DOCUMENT_SECTIONS = {
    "GOVERNANCE": {
        "title": "I. GOVERNANCE & STRUCTURE",
        "keywords": ["board", "committee", "bylaws", "governance"],
        "suggested_images": [3, 4, 5]
    },
    "MOUNTAIN_HOME": {
        "title": "II. A MOUNTAIN HOME", 
        "keywords": ["mountain", "home", "property", "landscape"],
        "suggested_images": [1, 2]
    },
    "WOOD_CHIPPING": {
        "title": "III. WOOD-CHIPPING PROGRAM",
        "keywords": ["wood", "chip", "debris", "brush"],
        "suggested_images": []
    },
    "FIRE_SAFETY": {
        "title": "IV. FIRE SAFETY & EMERGENCY PREPAREDNESS",
        "keywords": ["fire", "emergency", "evacuation", "safety"],
        "suggested_images": [6, 7, 8]
    },
    "COMMUNITY_SERVICES": {
        "title": "V. COMMUNITY SERVICES & AMENITIES",
        "keywords": ["service", "amenity", "internet", "road"],
        "suggested_images": []
    },
    "DEER_LAKE": {
        "title": "VI. DEER LAKE RECREATION AREA",
        "keywords": ["lake", "recreation", "swimming", "beach"],
        "suggested_images": [9, 10, 11, 12]
    },
    "LODGE": {
        "title": "VII. THE LODGE",
        "keywords": ["lodge", "facility", "rental", "event"],
        "suggested_images": []
    }
}

@app.route('/api/v1/document/<doc_id>/images/analyze', methods=['GET'])
def analyze_images(doc_id):
    """Get detailed image analysis with placement suggestions"""
    try:
        doc_result = api.get_document(doc_id)
        if not doc_result['success']:
            raise Exception('Failed to get document')
        
        document = doc_result['document']
        content = document.get('body', {}).get('content', [])
        inline_objects = document.get('inlineObjects', {})
        
        images = []
        image_positions = {}
        
        # Find image positions
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for elem in paragraph.get('elements', []):
                    if 'inlineObjectElement' in elem:
                        obj_id = elem['inlineObjectElement']['inlineObjectId']
                        image_positions[obj_id] = {
                            'start_index': elem.get('startIndex', 0),
                            'end_index': elem.get('endIndex', 0),
                            'paragraph_index': element.get('startIndex', 0)
                        }
        
        # Analyze each image
        for idx, (obj_id, obj) in enumerate(inline_objects.items(), 1):
            props = obj.get('inlineObjectProperties', {})
            embedded = props.get('embeddedObject', {})
            size = embedded.get('size', {})
            
            position = image_positions.get(obj_id, {})
            
            # Determine suggested section
            suggested_section = None
            for section_key, section_info in DOCUMENT_SECTIONS.items():
                if idx in section_info['suggested_images']:
                    suggested_section = section_key
                    break
            
            images.append({
                'id': obj_id,
                'index': idx,
                'title': embedded.get('title', f'Image {idx}'),
                'description': embedded.get('description', ''),
                'width': size.get('width', {}).get('magnitude', 0),
                'height': size.get('height', {}).get('magnitude', 0),
                'position': position,
                'needs_resize': size.get('width', {}).get('magnitude', 0) > 400,
                'suggested_section': suggested_section,
                'current_location': 'document_start' if position.get('start_index', 0) < 100 else 'document_body'
            })
        
        # Group images by location
        clustered_images = []
        for i, img in enumerate(images):
            if i > 0 and img['position']['start_index'] - images[i-1]['position']['end_index'] < 10:
                if not clustered_images or clustered_images[-1][-1]['index'] == images[i-1]['index']:
                    if clustered_images and clustered_images[-1][-1]['index'] == images[i-1]['index']:
                        clustered_images[-1].append(img)
                    else:
                        clustered_images.append([images[i-1], img])
        
        return jsonify({
            'success': True,
            'total_images': len(images),
            'images': images,
            'issues': {
                'oversized_count': sum(1 for img in images if img['needs_resize']),
                'clustered_groups': len(clustered_images),
                'missing_captions': sum(1 for img in images if not img['description'])
            },
            'suggestions': DOCUMENT_SECTIONS
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/document/<doc_id>/sections-with-indices', methods=['GET'])
def get_sections_with_indices(doc_id):
    """Get all document sections with their character indices"""
    try:
        doc_result = api.get_document(doc_id)
        if not doc_result['success']:
            raise Exception('Failed to get document')
        
        document = doc_result['document']
        content = document.get('body', {}).get('content', [])
        
        sections = []
        
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                text = ''
                
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text += elem['textRun'].get('content', '')
                
                # Check if it's a section header
                text = text.strip()
                if text and text.isupper() and 10 < len(text) < 100:
                    # Match with known sections
                    section_key = None
                    for key, info in DOCUMENT_SECTIONS.items():
                        if any(keyword in text.lower() for keyword in info['keywords']):
                            section_key = key
                            break
                    
                    sections.append({
                        'title': text,
                        'key': section_key,
                        'start_index': element.get('startIndex', 0),
                        'end_index': element.get('endIndex', 0),
                        'paragraph_count': 0,
                        'current_images': []
                    })
        
        return jsonify({
            'success': True,
            'sections': sections,
            'total_sections': len(sections)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/document/<doc_id>/image/<image_id>/move', methods=['POST'])
def move_image(doc_id, image_id):
    """Move an image to a specific location"""
    try:
        data = request.json
        target_section = data.get('target_section')
        position_type = data.get('position_type', 'after_header')  # after_header, before_section_end
        
        # This would require complex document manipulation
        # For now, return the plan
        return jsonify({
            'success': True,
            'message': 'Image movement planned',
            'image_id': image_id,
            'target_section': target_section,
            'position_type': position_type,
            'note': 'Use Google Apps Script for actual movement'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/document/<doc_id>/images/batch-resize', methods=['POST'])
def batch_resize_images(doc_id):
    """Generate Apps Script for batch image resize"""
    try:
        script = f'''
function resizeAllDocumentImages() {{
  var doc = DocumentApp.openById('{doc_id}');
  var body = doc.getBody();
  var images = body.getImages();
  
  var MAX_WIDTH = 400;
  var resizedCount = 0;
  
  images.forEach(function(image, index) {{
    var width = image.getWidth();
    var height = image.getHeight();
    
    if (width > MAX_WIDTH) {{
      var ratio = MAX_WIDTH / width;
      var newHeight = Math.round(height * ratio);
      
      image.setWidth(MAX_WIDTH);
      image.setHeight(newHeight);
      
      // Center the image
      var parent = image.getParent();
      if (parent.getType() === DocumentApp.ElementType.PARAGRAPH) {{
        parent.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
        parent.setSpacingBefore(12);
        parent.setSpacingAfter(12);
      }}
      
      resizedCount++;
      
      Logger.log('Resized image ' + (index + 1) + ': ' + width + 'x' + height + ' → ' + MAX_WIDTH + 'x' + newHeight);
    }}
  }});
  
  doc.saveAndClose();
  
  return {{
    'total_images': images.length,
    'resized_count': resizedCount
  }};
}}

// Run this function
resizeAllDocumentImages();
'''
        
        return jsonify({
            'success': True,
            'apps_script': script,
            'instructions': [
                'Open the document in Google Docs',
                'Go to Extensions → Apps Script',
                'Paste this script and run it',
                'All images will be resized to 400pt max width'
            ]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/document/<doc_id>/images/redistribute', methods='POST')
def generate_redistribution_script(doc_id):
    """Generate Apps Script to redistribute images throughout document"""
    try:
        script = '''
function redistributeImages() {
  var doc = DocumentApp.openById('%s');
  var body = doc.getBody();
  
  // Define section mappings
  var sectionMappings = {
    'A MOUNTAIN HOME': [0, 1],  // Images 1-2
    'GOVERNANCE': [2, 3, 4],     // Images 3-5
    'FIRE SAFETY': [5, 6, 7],    // Images 6-8
    'DEER LAKE': [8, 9, 10, 11]  // Images 9-12
  };
  
  // Find sections and move images
  var paragraphs = body.getParagraphs();
  var images = body.getImages();
  var sectionIndices = {};
  
  // Find section headers
  paragraphs.forEach(function(para, index) {
    var text = para.getText();
    if (text && text === text.toUpperCase() && text.length > 10 && text.length < 100) {
      for (var section in sectionMappings) {
        if (text.indexOf(section) !== -1) {
          sectionIndices[section] = index;
        }
      }
    }
  });
  
  // Move images to appropriate sections
  // Note: This is simplified - actual implementation would need to handle moves carefully
  
  Logger.log('Section indices found: ' + JSON.stringify(sectionIndices));
  Logger.log('Ready to redistribute ' + images.length + ' images');
  
  return {
    'sections_found': Object.keys(sectionIndices).length,
    'images_to_move': images.length
  };
}
''' % doc_id
        
        return jsonify({
            'success': True,
            'apps_script': script,
            'note': 'This script identifies sections. Manual movement recommended for safety.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("AGENT 1 - Image Management API")
    print("=" * 60)
    print("\nEndpoints:")
    print("  GET  /api/v1/document/{id}/images/analyze")
    print("  GET  /api/v1/document/{id}/sections-with-indices")
    print("  POST /api/v1/document/{id}/image/{image_id}/move")
    print("  POST /api/v1/document/{id}/images/batch-resize")
    print("  POST /api/v1/document/{id}/images/redistribute")
    print("\nStarting on http://localhost:5002")
    print("=" * 60)
    
    app.run(debug=True, port=5002)