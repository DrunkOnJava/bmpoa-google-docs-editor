#!/bin/bash

# Setup script for AGENT 2
# This script prepares the worktree and environment for the second agent

echo "==================================="
echo "AGENT 2 WORKSPACE SETUP"
echo "==================================="

# Check if we're in the right directory
if [ ! -f "AGENT_WORKFLOW.md" ]; then
    echo "❌ Error: Must run from main project directory"
    exit 1
fi

# Create agent2 branch if it doesn't exist
if ! git show-ref --quiet refs/heads/agent2-frontend; then
    echo "📌 Creating agent2-frontend branch..."
    git branch agent2-frontend
fi

# Create worktree for agent2
if [ ! -d "../agent2-workspace" ]; then
    echo "🌳 Creating worktree for agent2..."
    git worktree add ../agent2-workspace agent2-frontend
    echo "✅ Worktree created at ../agent2-workspace"
else
    echo "ℹ️  Worktree already exists at ../agent2-workspace"
fi

# Create initial structure for agent2
cd ../agent2-workspace

# Create frontend directories
echo "📁 Creating frontend structure..."
mkdir -p src/components src/services src/utils public tests

# Create initial package.json for frontend
cat > package.json << 'EOF'
{
  "name": "bmpoa-docs-frontend",
  "version": "1.0.0",
  "description": "Frontend for BMPOA Google Docs Editor",
  "main": "index.js",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "jest"
  },
  "keywords": ["google-docs", "editor", "bmpoa"],
  "author": "AGENT 2",
  "license": "MIT",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "socket.io-client": "^4.5.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^4.4.0"
  }
}
EOF

# Create README for agent2
cat > README_AGENT2.md << 'EOF'
# AGENT 2 - Frontend Development

This is the workspace for AGENT 2, responsible for frontend development.

## Current Status
- Branch: `agent2-frontend`
- Focus: UI/UX Development

## Setup
```bash
npm install
npm run dev
```

## Communication
- Check `shared/status.json` for coordination
- Update status regularly
- Pull from main branch frequently

## Tasks
See `shared/tasks.json` for assigned tasks.
EOF

# Create a simple index.html
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BMPOA Docs Editor - Frontend</title>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
</body>
</html>
EOF

# Update agent2 status
cd ../bmpoa-google-docs-editor
cat > shared/status.json << 'EOF'
{
  "agent1": {
    "status": "active",
    "current_task": "API development",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  },
  "agent2": {
    "status": "ready",
    "current_task": "Frontend setup",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "workspace": "../agent2-workspace"
  }
}
EOF

echo ""
echo "✅ AGENT 2 workspace is ready!"
echo ""
echo "📋 Instructions for AGENT 2:"
echo "1. Navigate to: cd ../agent2-workspace"
echo "2. Check tasks: cat ../bmpoa-google-docs-editor/shared/tasks.json"
echo "3. Update status: edit ../bmpoa-google-docs-editor/shared/status.json"
echo "4. Start development: npm install && npm run dev"
echo ""
echo "🔄 Sync commands:"
echo "   git pull origin main"
echo "   git push origin agent2-frontend"
echo ""