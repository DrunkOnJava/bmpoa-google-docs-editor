# Contributing to BMPOA Google Docs Editor

Thank you for considering contributing to the BMPOA Google Docs Editor! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our code of conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/bmpoa-google-docs-editor.git
   cd bmpoa-google-docs-editor
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/bmpoa-google-docs-editor.git
   ```
4. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📋 Development Process

### 1. Check existing issues
- Look for existing issues or create a new one
- Comment on the issue to indicate you're working on it

### 2. Development setup
```bash
# Create virtual environment
python3 -m venv gdocs_env
source gdocs_env/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r api/requirements.txt

# Install development dependencies
pip install pytest pytest-cov flake8 black
```

### 3. Make your changes
- Write clean, readable code
- Follow PEP 8 style guidelines
- Add docstrings to functions and classes
- Update documentation as needed

### 4. Test your changes
```bash
# Run tests
pytest tests/

# Check code style
flake8 .
black --check .

# Format code
black .
```

### 5. Commit your changes
```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add new document search functionality"
```

#### Commit message format:
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `style:` code style changes (formatting, etc.)
- `refactor:` code refactoring
- `test:` test additions or modifications
- `chore:` maintenance tasks

### 6. Push and create Pull Request
```bash
# Push to your fork
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 📝 Pull Request Guidelines

### PR Title
Use the same format as commit messages: `type: description`

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for new features
- [ ] Updated documentation

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Fixes #123
```

## 🧪 Testing Guidelines

### Unit Tests
- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Use pytest for testing

### Example test:
```python
def test_document_analysis():
    tool = BMPOADocumentTool()
    result = tool.analyze_document()
    assert result is not None
    assert 'statistics' in result
```

## 📚 Documentation

- Update README.md if adding new features
- Add docstrings to all functions:
  ```python
  def process_document(doc_id: str) -> Dict:
      """
      Process a Google Doc and return analysis.
      
      Args:
          doc_id: The Google Doc ID
          
      Returns:
          Dict containing document analysis
      """
  ```
- Update API documentation for new endpoints

## 🏗️ Architecture Guidelines

### File Organization
- API code goes in `api/`
- Shared utilities in `shared/`
- Tests in `tests/`
- Documentation in `docs/`

### Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

## 🔄 Multi-Agent Development

If working as part of the multi-agent system:

1. **Update your status** in `shared/status.json`
2. **Check task assignments** in `shared/tasks.json`
3. **Coordinate through commits** with clear messages
4. **Use feature branches** for parallel work

## 🐛 Reporting Issues

### Bug Reports
Include:
- Python version
- OS information
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative solutions considered

## 📞 Getting Help

- Check existing documentation
- Search closed issues
- Ask in discussions
- Tag maintainers in complex issues

## 🎉 Recognition

Contributors will be added to the AUTHORS file and recognized in release notes.

Thank you for contributing! 🙏