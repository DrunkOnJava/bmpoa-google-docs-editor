# Frontend Integration Examples

Since AGENT 2 has the frontend running on localhost:3000, here are integration examples:

## 🔌 Connecting to the Backend APIs

### 1. REST API Integration

```javascript
// Frontend API service (for AGENT 2)
const API_BASE = 'http://localhost:5000/api/v1';

// Get document content
async function getDocumentContent(docId) {
  const response = await fetch(`${API_BASE}/document/${docId}/content`);
  return response.json();
}

// Search in document
async function searchDocument(docId, query) {
  const response = await fetch(`${API_BASE}/document/${docId}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  return response.json();
}

// Get document images
async function getDocumentImages(docId) {
  const response = await fetch(`${API_BASE}/document/${docId}/images`);
  return response.json();
}

// Update document
async function updateDocument(docId, operations) {
  const response = await fetch(`${API_BASE}/document/${docId}/update`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ operations })
  });
  return response.json();
}
```

### 2. WebSocket Integration

```javascript
// WebSocket connection for real-time collaboration
import io from 'socket.io-client';

const socket = io('ws://localhost:5001');

// Join as agent
socket.emit('agent_join', { 
  agent_id: 'agent2-frontend',
  name: 'Frontend Client'
});

// Listen for document changes
socket.on('document_changed', (data) => {
  console.log('Document updated:', data);
  // Update your preview component
});

// Send document updates
function sendDocumentUpdate(updateType, data) {
  socket.emit('document_update', {
    type: updateType,
    data: data
  });
}

// Update task status
function updateTaskStatus(taskId, status) {
  socket.emit('task_update', {
    task_id: taskId,
    status: status
  });
}
```

### 3. Image Gallery Integration

```javascript
// For the completed Image Gallery component
import { useState, useEffect } from 'react';

function DocumentImageGallery({ documentId }) {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadImages() {
      try {
        const response = await fetch(
          `http://localhost:5000/api/v1/document/${documentId}/images`
        );
        const data = await response.json();
        if (data.success) {
          setImages(data.images);
        }
      } catch (error) {
        console.error('Failed to load images:', error);
      } finally {
        setLoading(false);
      }
    }

    loadImages();
  }, [documentId]);

  return (
    <div className="image-gallery">
      {loading ? (
        <div>Loading images...</div>
      ) : (
        <div className="image-grid">
          {images.map((image) => (
            <div key={image.id} className="image-item">
              <img 
                src={image.url} 
                alt={image.title}
                style={{
                  maxWidth: '200px',
                  height: 'auto'
                }}
              />
              <div className="image-info">
                <p>{image.title}</p>
                <small>{image.width}x{image.height}</small>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### 4. Document Preview Component Integration

```javascript
// For task-002: Document Preview Component
import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

function DocumentPreview({ documentId }) {
  const [content, setContent] = useState('');
  const [structure, setStructure] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Connect to WebSocket for live updates
    const socket = io('ws://localhost:5001');
    
    socket.on('document_changed', (update) => {
      // Refresh content on changes
      loadDocument();
    });

    loadDocument();

    return () => socket.disconnect();
  }, [documentId]);

  async function loadDocument() {
    try {
      // Get content
      const contentRes = await fetch(
        `http://localhost:5000/api/v1/document/${documentId}/content`
      );
      const contentData = await contentRes.json();

      // Get structure
      const structureRes = await fetch(
        `http://localhost:5000/api/v1/document/${documentId}/structure`
      );
      const structureData = await structureRes.json();

      if (contentData.success) {
        setContent(contentData.content);
      }
      if (structureData.success) {
        setStructure(structureData.structure);
      }
    } catch (error) {
      console.error('Failed to load document:', error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="document-preview">
      {loading ? (
        <div>Loading document...</div>
      ) : (
        <>
          <div className="document-stats">
            <span>Sections: {structure?.sections.length || 0}</span>
            <span>Images: {structure?.images.length || 0}</span>
            <span>Tables: {structure?.tables.length || 0}</span>
          </div>
          <div className="document-content">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        </>
      )}
    </div>
  );
}
```

## 🚀 Quick Start for Integration

1. **Start Backend Services** (AGENT 1):
```bash
# Terminal 1: REST API
python api/document_api.py

# Terminal 2: WebSocket Server
python api/websocket_server.py
```

2. **Frontend Connection** (AGENT 2):
- API available at: http://localhost:5000
- WebSocket available at: ws://localhost:5001
- CORS is enabled for all origins

3. **Test the Integration**:
```bash
# Test API endpoint
curl http://localhost:5000/api/v1/status/agents

# Should return current agent status
```

## 📝 Available Document ID for Testing

Use this document ID for all API calls:
```
169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs
```

## 🔄 Real-time Collaboration Flow

1. Frontend connects to WebSocket
2. Frontend joins as agent
3. Any document updates are broadcast to all connected agents
4. Frontend updates UI based on received events

The backend is ready and waiting for frontend connections!