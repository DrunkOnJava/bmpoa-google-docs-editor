#!/usr/bin/env python3
"""
AGENT 1 - WebSocket Server for Real-time Collaboration
Handles real-time document updates and agent communication
"""

from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bmpoa-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Active connections
active_agents = {}
document_room = "bmpoa-document"

@socketio.on('connect')
def handle_connect():
    """Handle new connection"""
    print(f"New connection: {request.sid}")
    emit('connected', {'sid': request.sid})

@socketio.on('agent_join')
def handle_agent_join(data):
    """Agent joins the collaboration"""
    agent_id = data.get('agent_id')
    active_agents[request.sid] = {
        'agent_id': agent_id,
        'connected_at': datetime.utcnow().isoformat()
    }
    
    # Join document room
    join_room(document_room)
    
    # Notify other agents
    emit('agent_joined', {
        'agent_id': agent_id,
        'timestamp': datetime.utcnow().isoformat()
    }, room=document_room, skip_sid=request.sid)
    
    print(f"Agent {agent_id} joined")

@socketio.on('document_update')
def handle_document_update(data):
    """Broadcast document updates to all agents"""
    update = {
        'agent_id': active_agents.get(request.sid, {}).get('agent_id', 'unknown'),
        'update_type': data.get('type'),
        'data': data.get('data'),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Broadcast to all agents in room
    emit('document_changed', update, room=document_room, skip_sid=request.sid)
    
    print(f"Document update from {update['agent_id']}: {update['update_type']}")

@socketio.on('sync_request')
def handle_sync_request(data):
    """Handle synchronization requests between agents"""
    requesting_agent = active_agents.get(request.sid, {}).get('agent_id', 'unknown')
    
    emit('sync_needed', {
        'requesting_agent': requesting_agent,
        'sync_type': data.get('type'),
        'timestamp': datetime.utcnow().isoformat()
    }, room=document_room)

@socketio.on('task_update')
def handle_task_update(data):
    """Update task status and notify agents"""
    task_id = data.get('task_id')
    new_status = data.get('status')
    agent_id = active_agents.get(request.sid, {}).get('agent_id', 'unknown')
    
    # Update tasks.json
    tasks_path = '../shared/tasks.json'
    with open(tasks_path, 'r') as f:
        tasks_data = json.load(f)
    
    for task in tasks_data['tasks']:
        if task['id'] == task_id:
            task['status'] = new_status
            task['last_updated_by'] = agent_id
            break
    
    tasks_data['last_updated'] = datetime.utcnow().isoformat()
    
    with open(tasks_path, 'w') as f:
        json.dump(tasks_data, f, indent=2)
    
    # Notify all agents
    emit('task_updated', {
        'task_id': task_id,
        'new_status': new_status,
        'updated_by': agent_id,
        'timestamp': datetime.utcnow().isoformat()
    }, room=document_room)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle agent disconnect"""
    if request.sid in active_agents:
        agent_id = active_agents[request.sid]['agent_id']
        del active_agents[request.sid]
        
        # Notify others
        emit('agent_left', {
            'agent_id': agent_id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=document_room)
        
        print(f"Agent {agent_id} disconnected")

if __name__ == '__main__':
    print("AGENT 1 - WebSocket Server Starting...")
    print("Real-time collaboration available at ws://localhost:5001")
    socketio.run(app, debug=True, port=5001)