#!/usr/bin/env python3
"""
AGENT 1 - Collaborative Document Editor Backend
Real-time collaborative editing with operational transformation
"""

import json
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

class OperationType(Enum):
    INSERT = "insert"
    DELETE = "delete"
    FORMAT = "format"
    CURSOR = "cursor"

@dataclass
class Operation:
    """Represents a document operation"""
    op_type: OperationType
    position: int
    content: Optional[str] = None
    length: Optional[int] = None
    attributes: Optional[Dict] = None
    agent_id: str = ""
    timestamp: str = ""
    op_id: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if not self.op_id:
            # Generate unique operation ID
            data = f"{self.op_type.value}{self.position}{self.timestamp}{self.agent_id}"
            self.op_id = hashlib.md5(data.encode()).hexdigest()[:8]

class DocumentState:
    """Maintains document state and handles transformations"""
    
    def __init__(self, document_id: str):
        self.document_id = document_id
        self.content = ""
        self.version = 0
        self.operations: List[Operation] = []
        self.pending_operations: Dict[str, List[Operation]] = {}
        self.lock = threading.Lock()
        
    def apply_operation(self, op: Operation) -> bool:
        """Apply an operation to the document"""
        with self.lock:
            try:
                if op.op_type == OperationType.INSERT:
                    if op.content and 0 <= op.position <= len(self.content):
                        self.content = (
                            self.content[:op.position] + 
                            op.content + 
                            self.content[op.position:]
                        )
                        self.version += 1
                        self.operations.append(op)
                        return True
                        
                elif op.op_type == OperationType.DELETE:
                    if op.length and 0 <= op.position < len(self.content):
                        end_pos = min(op.position + op.length, len(self.content))
                        self.content = (
                            self.content[:op.position] + 
                            self.content[end_pos:]
                        )
                        self.version += 1
                        self.operations.append(op)
                        return True
                        
                elif op.op_type == OperationType.FORMAT:
                    # Format operations don't change content
                    self.version += 1
                    self.operations.append(op)
                    return True
                    
                return False
                
            except Exception as e:
                print(f"Error applying operation: {e}")
                return False
    
    def transform_operation(self, op1: Operation, op2: Operation) -> Operation:
        """Transform op1 against op2 for operational transformation"""
        # Simplified OT implementation
        if op1.op_type == OperationType.INSERT and op2.op_type == OperationType.INSERT:
            if op1.position < op2.position:
                return op1
            elif op1.position > op2.position:
                return Operation(
                    op_type=op1.op_type,
                    position=op1.position + len(op2.content or ""),
                    content=op1.content,
                    agent_id=op1.agent_id
                )
            else:
                # Same position - use agent_id for consistency
                if op1.agent_id < op2.agent_id:
                    return op1
                else:
                    return Operation(
                        op_type=op1.op_type,
                        position=op1.position + len(op2.content or ""),
                        content=op1.content,
                        agent_id=op1.agent_id
                    )
                    
        elif op1.op_type == OperationType.DELETE and op2.op_type == OperationType.INSERT:
            if op1.position < op2.position:
                return op1
            else:
                return Operation(
                    op_type=op1.op_type,
                    position=op1.position + len(op2.content or ""),
                    length=op1.length,
                    agent_id=op1.agent_id
                )
                
        elif op1.op_type == OperationType.INSERT and op2.op_type == OperationType.DELETE:
            if op1.position <= op2.position:
                return op1
            elif op1.position > op2.position + (op2.length or 0):
                return Operation(
                    op_type=op1.op_type,
                    position=op1.position - (op2.length or 0),
                    content=op1.content,
                    agent_id=op1.agent_id
                )
            else:
                return Operation(
                    op_type=op1.op_type,
                    position=op2.position,
                    content=op1.content,
                    agent_id=op1.agent_id
                )
                
        # Default: return original
        return op1
    
    def get_state(self) -> Dict:
        """Get current document state"""
        with self.lock:
            return {
                'document_id': self.document_id,
                'content': self.content,
                'version': self.version,
                'length': len(self.content),
                'last_operation': asdict(self.operations[-1]) if self.operations else None
            }

class CollaborativeSession:
    """Manages a collaborative editing session"""
    
    def __init__(self, document_id: str):
        self.document_id = document_id
        self.document_state = DocumentState(document_id)
        self.connected_agents: Dict[str, Dict] = {}
        self.cursor_positions: Dict[str, int] = {}
        self.selection_ranges: Dict[str, Tuple[int, int]] = {}
        
    def add_agent(self, agent_id: str, agent_info: Dict):
        """Add an agent to the session"""
        self.connected_agents[agent_id] = {
            **agent_info,
            'joined_at': datetime.utcnow().isoformat()
        }
        self.cursor_positions[agent_id] = 0
        
    def remove_agent(self, agent_id: str):
        """Remove an agent from the session"""
        if agent_id in self.connected_agents:
            del self.connected_agents[agent_id]
        if agent_id in self.cursor_positions:
            del self.cursor_positions[agent_id]
        if agent_id in self.selection_ranges:
            del self.selection_ranges[agent_id]
    
    def update_cursor(self, agent_id: str, position: int):
        """Update agent's cursor position"""
        self.cursor_positions[agent_id] = position
        
    def update_selection(self, agent_id: str, start: int, end: int):
        """Update agent's selection range"""
        self.selection_ranges[agent_id] = (start, end)
    
    def get_session_info(self) -> Dict:
        """Get current session information"""
        return {
            'document_id': self.document_id,
            'connected_agents': list(self.connected_agents.keys()),
            'agent_count': len(self.connected_agents),
            'document_version': self.document_state.version,
            'cursor_positions': self.cursor_positions,
            'selection_ranges': self.selection_ranges
        }

class CollaborationManager:
    """Manages multiple collaborative sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, CollaborativeSession] = {}
        self.operation_queue: List[Tuple[str, Operation]] = []
        self.lock = threading.Lock()
        
    def create_session(self, document_id: str, initial_content: str = "") -> CollaborativeSession:
        """Create a new collaborative session"""
        with self.lock:
            if document_id not in self.sessions:
                session = CollaborativeSession(document_id)
                session.document_state.content = initial_content
                self.sessions[document_id] = session
            return self.sessions[document_id]
    
    def get_session(self, document_id: str) -> Optional[CollaborativeSession]:
        """Get an existing session"""
        return self.sessions.get(document_id)
    
    def process_operation(self, document_id: str, operation: Operation) -> Dict:
        """Process an operation from an agent"""
        session = self.get_session(document_id)
        if not session:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        # Apply operation
        success = session.document_state.apply_operation(operation)
        
        if success:
            # Queue for broadcast
            with self.lock:
                self.operation_queue.append((document_id, operation))
            
            return {
                'success': True,
                'new_version': session.document_state.version,
                'operation_id': operation.op_id
            }
        else:
            return {
                'success': False,
                'error': 'Failed to apply operation'
            }
    
    def get_pending_operations(self, document_id: str, since_version: int) -> List[Operation]:
        """Get operations since a specific version"""
        session = self.get_session(document_id)
        if not session:
            return []
        
        with session.document_state.lock:
            return [
                op for op in session.document_state.operations
                if session.document_state.operations.index(op) >= since_version
            ]

# Example usage for testing
if __name__ == "__main__":
    # Create collaboration manager
    collab = CollaborationManager()
    
    # Create a session
    doc_id = "test-doc-123"
    session = collab.create_session(doc_id, "Hello World")
    
    # Add agents
    session.add_agent("agent1", {"name": "Agent 1"})
    session.add_agent("agent2", {"name": "Agent 2"})
    
    # Simulate operations
    op1 = Operation(
        op_type=OperationType.INSERT,
        position=5,
        content=" Beautiful",
        agent_id="agent1"
    )
    
    result = collab.process_operation(doc_id, op1)
    print(f"Operation result: {result}")
    print(f"Document state: {session.document_state.get_state()}")
    
    # Get session info
    print(f"Session info: {session.get_session_info()}")