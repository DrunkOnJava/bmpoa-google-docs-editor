#!/usr/bin/env python3
"""
AGENT 1 - API Server for BMPOA Google Docs Editor
Provides REST API endpoints for document operations
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import sys
sys.path.append('..')

from bmpoa_service_account_tool import BMPOADocumentTool

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize document tool
doc_tool = BMPOADocumentTool()
doc_tool.authenticate()

# Shared data path
SHARED_PATH = '../shared/'

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status"""
    with open(os.path.join(SHARED_PATH, 'status.json'), 'r') as f:
        status = json.load(f)
    return jsonify(status)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get task list"""
    with open(os.path.join(SHARED_PATH, 'tasks.json'), 'r') as f:
        tasks = json.load(f)
    return jsonify(tasks)

@app.route('/api/document/analyze', methods=['GET'])
def analyze_document():
    """Analyze the BMPOA document"""
    try:
        analysis = doc_tool.analyze_document()
        return jsonify({
            'success': True,
            'data': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/document/search', methods=['POST'])
def search_document():
    """Search for text in document"""
    try:
        data = request.json
        search_term = data.get('query', '')
        results = doc_tool.search_text(search_term)
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/document/images', methods=['GET'])
def get_images():
    """Get all document images"""
    try:
        # This would need implementation in the tool
        return jsonify({
            'success': True,
            'images': [],  # Placeholder
            'message': 'Image API endpoint ready for AGENT 2'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agent/update', methods=['POST'])
def update_agent_status():
    """Update agent status"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        status_update = data.get('status')
        
        # Read current status
        with open(os.path.join(SHARED_PATH, 'status.json'), 'r') as f:
            status = json.load(f)
        
        # Update specific agent
        if agent_id in status:
            status[agent_id].update(status_update)
            status[agent_id]['timestamp'] = data.get('timestamp')
        
        # Write back
        with open(os.path.join(SHARED_PATH, 'status.json'), 'w') as f:
            json.dump(status, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Status updated for {agent_id}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("AGENT 1 - API Server Starting...")
    print("Endpoints available at http://localhost:5000/api/")
    app.run(debug=True, port=5000)