#!/usr/bin/env python3
"""
AGENT 1 - Enhanced Document API
Comprehensive REST API for document operations
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime
import io

sys.path.append('..')
from bmpoa_service_account_tool import BMPOADocumentTool
from enhanced_gdocs_api import EnhancedGoogleDocsAPI

app = Flask(__name__)
CORS(app)

# Initialize tools
doc_tool = BMPOADocumentTool()
enhanced_api = EnhancedGoogleDocsAPI()

# Authenticate both tools
doc_tool.authenticate()
enhanced_api.authenticate()

@app.route('/api/v1/document/<doc_id>/content', methods=['GET'])
def get_document_content(doc_id):
    """Get full document content"""
    try:
        content = enhanced_api.extract_document_text(doc_id)
        
        return jsonify({
            'success': True,
            'document_id': doc_id,
            'content': content,
            'length': len(content)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/document/<doc_id>/structure', methods=['GET'])
def get_document_structure(doc_id):
    """Get document structure with sections and images"""
    try:
        # Get document
        doc_result = enhanced_api.get_document(doc_id)
        if not doc_result['success']:
            raise Exception(doc_result.get('error', 'Failed to get document'))
        
        document = doc_result['document']
        content = document.get('body', {}).get('content', [])
        
        structure = {
            'sections': [],
            'images': [],
            'tables': [],
            'lists': []
        }
        
        current_section = None
        
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                text = ''
                
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text += elem['textRun'].get('content', '')
                    elif 'inlineObjectElement' in elem:
                        structure['images'].append({
                            'id': elem['inlineObjectElement']['inlineObjectId'],
                            'position': elem.get('startIndex', 0)
                        })
                
                # Check if section header
                if text.strip() and text.strip().isupper() and len(text.strip()) < 100:
                    current_section = {
                        'title': text.strip(),
                        'start_index': element.get('startIndex', 0),
                        'content': []
                    }
                    structure['sections'].append(current_section)
                elif current_section and text.strip():
                    current_section['content'].append(text.strip())
            
            elif 'table' in element:
                structure['tables'].append({
                    'position': element.get('startIndex', 0),
                    'rows': element['table'].get('rows', 0),
                    'columns': element['table'].get('columns', 0)
                })
        
        return jsonify({
            'success': True,
            'document_id': doc_id,
            'structure': structure,
            'statistics': {
                'sections': len(structure['sections']),
                'images': len(structure['images']),
                'tables': len(structure['tables'])
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/document/<doc_id>/search', methods=['POST'])
def search_in_document(doc_id):
    """Search for text in document"""
    try:
        data = request.json
        query = data.get('query', '')
        case_sensitive = data.get('case_sensitive', False)
        
        # Find text
        ranges = enhanced_api.find_text_indices(doc_id, query)
        
        results = []
        for text_range in ranges:
            results.append({
                'start': text_range.start_index,
                'end': text_range.end_index,
                'length': text_range.end_index - text_range.start_index
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'matches': len(results),
            'results': results[:50]  # Limit to 50 results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/document/<doc_id>/update', methods=['POST'])
def update_document(doc_id):
    """Update document with batch operations"""
    try:
        data = request.json
        operations = data.get('operations', [])
        
        # Queue operations
        for op in operations:
            op_type = op.get('type')
            
            if op_type == 'insert_text':
                enhanced_api.insert_text(op['text'], op['index'])
            
            elif op_type == 'delete_text':
                enhanced_api.delete_content(op['start'], op['end'])
            
            elif op_type == 'format_text':
                style = op.get('style', {})
                enhanced_api.update_text_style(
                    op['start'], 
                    op['end'],
                    style
                )
            
            elif op_type == 'replace_all':
                enhanced_api.replace_all_text(
                    op['search'],
                    op['replace'],
                    op.get('match_case', False)
                )
        
        # Execute batch
        result = enhanced_api.execute_batch(doc_id)
        
        return jsonify({
            'success': result['success'],
            'operations_executed': result.get('executed_requests', 0),
            'message': 'Document updated successfully' if result['success'] else result.get('error')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/document/<doc_id>/images', methods=['GET'])
def get_document_images(doc_id):
    """Get all images in document"""
    try:
        doc_result = enhanced_api.get_document(doc_id)
        if not doc_result['success']:
            raise Exception('Failed to get document')
        
        document = doc_result['document']
        inline_objects = document.get('inlineObjects', {})
        
        images = []
        for obj_id, obj in inline_objects.items():
            props = obj.get('inlineObjectProperties', {})
            embedded = props.get('embeddedObject', {})
            size = embedded.get('size', {})
            
            images.append({
                'id': obj_id,
                'title': embedded.get('title', 'Untitled'),
                'description': embedded.get('description', ''),
                'width': size.get('width', {}).get('magnitude', 0),
                'height': size.get('height', {}).get('magnitude', 0),
                'url': embedded.get('imageProperties', {}).get('contentUri', '')
            })
        
        return jsonify({
            'success': True,
            'document_id': doc_id,
            'total_images': len(images),
            'images': images
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/status/agents', methods=['GET'])
def get_agents_status():
    """Get status of all agents"""
    try:
        with open('../shared/status.json', 'r') as f:
            status = json.load(f)
        
        # Add API server status
        status['api_server'] = {
            'status': 'running',
            'endpoints_active': 6,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/tasks', methods=['GET'])
def get_all_tasks():
    """Get all tasks with current status"""
    try:
        with open('../shared/tasks.json', 'r') as f:
            tasks = json.load(f)
        
        # Add progress info
        total_tasks = len(tasks['tasks'])
        completed = len([t for t in tasks['tasks'] if t['status'] == 'completed'])
        in_progress = len([t for t in tasks['tasks'] if t['status'] == 'in_progress'])
        
        return jsonify({
            'success': True,
            'tasks': tasks['tasks'],
            'summary': {
                'total': total_tasks,
                'completed': completed,
                'in_progress': in_progress,
                'pending': total_tasks - completed - in_progress
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update task status"""
    try:
        data = request.json
        new_status = data.get('status')
        
        # Read tasks
        with open('../shared/tasks.json', 'r') as f:
            tasks_data = json.load(f)
        
        # Update task
        task_found = False
        for task in tasks_data['tasks']:
            if task['id'] == task_id:
                task['status'] = new_status
                task['last_updated'] = datetime.utcnow().isoformat()
                task_found = True
                break
        
        if not task_found:
            return jsonify({
                'success': False,
                'error': f'Task {task_id} not found'
            }), 404
        
        # Save
        with open('../shared/tasks.json', 'w') as f:
            json.dump(tasks_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'new_status': new_status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("AGENT 1 - Document API Server")
    print("=" * 60)
    print("\nEndpoints available:")
    print("  GET  /api/v1/document/{id}/content")
    print("  GET  /api/v1/document/{id}/structure") 
    print("  POST /api/v1/document/{id}/search")
    print("  POST /api/v1/document/{id}/update")
    print("  GET  /api/v1/document/{id}/images")
    print("  GET  /api/v1/status/agents")
    print("  GET  /api/v1/tasks")
    print("  PUT  /api/v1/tasks/{id}")
    print("\nStarting server on http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, port=5000)