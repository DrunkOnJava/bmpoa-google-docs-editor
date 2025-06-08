# BMPOA Google Docs Editor

A comprehensive Google Docs editing and management system for the Blue Mountain Property Owners Association (BMPOA) documentation.

## 🚀 Features

- **Google Docs API Integration**: Full read/write access to Google Docs
- **Image Management**: Analyze, resize, and organize document images
- **Real-time Collaboration**: WebSocket-based collaborative editing
- **REST API**: Comprehensive API for document operations
- **Multi-Agent Architecture**: Supports parallel development with Git worktrees

## 📋 Prerequisites

- Python 3.8+
- Google Cloud Project with Docs API enabled
- Service Account credentials
- Node.js 16+ (for frontend development)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/[username]/bmpoa-google-docs-editor.git
cd bmpoa-google-docs-editor
```

2. **Set up Python environment**
```bash
python3 -m venv gdocs_env
source gdocs_env/bin/activate  # On Windows: gdocs_env\Scripts\activate
pip install -r requirements.txt
```

3. **Configure authentication**
   - Place your `service-account-key.json` in the project root
   - Ensure the service account has access to your Google Docs

## 🔧 Configuration

1. **Document ID**: Update the document ID in the configuration files:
```python
DOCUMENT_ID = "your-document-id-here"
```

2. **Service Account**: The service account email must have editor permissions on the target document.

## 📖 Usage

### Basic Document Operations
```bash
# Analyze document structure
python bmpoa_service_account_tool.py

# Run the API server
python api/document_api.py

# Start WebSocket server for collaboration
python api/websocket_server.py
```

### API Endpoints

- `GET /api/v1/document/{id}/content` - Get document content
- `GET /api/v1/document/{id}/structure` - Get document structure
- `POST /api/v1/document/{id}/search` - Search in document
- `POST /api/v1/document/{id}/update` - Update document
- `GET /api/v1/document/{id}/images` - Get all images

## 🤝 Multi-Agent Development

This project supports parallel development using Git worktrees:

```bash
# Set up second agent workspace
./setup-agent2.sh

# Agent communication via shared files
cat shared/status.json
cat shared/tasks.json
```

## 📁 Project Structure

```
bmpoa-google-docs-editor/
├── api/                    # REST API and WebSocket servers
├── shared/                 # Inter-agent communication
├── gdocs_env/             # Python virtual environment
├── *.py                   # Various document processing tools
└── *.gs                   # Google Apps Script files
```

## 🔒 Security

- Never commit credentials or keys
- Use environment variables for sensitive data
- Service account keys are gitignored

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👥 Authors

- AGENT 1 - Backend/API Development
- AGENT 2 - Frontend Development

## 🙏 Acknowledgments

- Blue Mountain Property Owners Association
- Google Docs API Team