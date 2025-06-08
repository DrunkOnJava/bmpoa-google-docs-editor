# Multi-Agent Workflow with Git Worktrees

## AGENT 1 (Current Instance) - Orchestrator & Backend
- **Branch**: `main`
- **Worktree**: Primary repository
- **Responsibilities**:
  - Project orchestration
  - Google Docs API integration
  - Image processing and analysis
  - Backend services

## AGENT 2 (New Instance) - Frontend & UI
- **Branch**: `agent2-frontend`
- **Worktree**: `agent2-workspace`
- **Responsibilities**:
  - User interface development
  - Document visualization
  - Real-time collaboration features
  - Frontend optimization

## Setup Instructions for AGENT 2

1. **Clone the repository**:
```bash
git clone [repository-url] bmpoa-google-docs-editor-agent2
cd bmpoa-google-docs-editor-agent2
```

2. **Create and checkout agent2 branch**:
```bash
git checkout -b agent2-frontend
```

3. **For worktree setup** (if using same local repo):
```bash
# From main repository
git worktree add ../agent2-workspace agent2-frontend
```

## Communication Protocol

### File-Based Communication
- **Shared Config**: `shared/config.json`
- **Task Queue**: `shared/tasks.json`
- **Status Updates**: `shared/status.json`

### Branch Strategy
- `main`: AGENT 1 primary development
- `agent2-frontend`: AGENT 2 development
- `integration`: Merged features from both agents
- `feature/*`: Individual feature branches

### Sync Points
1. **Every 30 minutes**: Pull latest changes
2. **Before major changes**: Create feature branch
3. **After completion**: Submit PR to integration

## Task Division

### AGENT 1 Tasks (Backend/API)
- [ ] Google Docs API integration
- [ ] Image processing pipeline
- [ ] Authentication management
- [ ] Data persistence layer
- [ ] API endpoints

### AGENT 2 Tasks (Frontend/UI)
- [ ] React/Vue frontend setup
- [ ] Document preview interface
- [ ] Image gallery component
- [ ] Real-time sync UI
- [ ] User authentication flow

## Git Commands Reference

### For AGENT 1:
```bash
# Create shared communication directory
mkdir -p shared
echo '{"agent1": "ready", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > shared/status.json

# Regular sync
git add shared/
git commit -m "AGENT1: Update status"
git push origin main
```

### For AGENT 2:
```bash
# After setup
git pull origin main
git merge main --no-ff

# Regular sync
git add .
git commit -m "AGENT2: [description]"
git push origin agent2-frontend
```

## Conflict Resolution
1. Always pull before pushing
2. Use feature branches for major changes
3. Communicate through commit messages
4. Use shared/status.json for real-time status

## Integration Workflow
```bash
# On integration branch
git checkout integration
git merge main --no-ff
git merge agent2-frontend --no-ff
# Resolve conflicts
git push origin integration
```