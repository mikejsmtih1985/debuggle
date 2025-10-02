# Contributing to Debuggle Core

Thank you for your interest in contributing to Debuggle Core! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- Git
- Virtual environment (recommended)

### Development Setup
1. **Fork and clone the repository:**
```bash
git clone https://github.com/yourusername/debuggle.git
cd debuggle
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install development dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run tests to ensure everything works:**
```bash
pytest
```

## 🔧 Development Workflow

### Branch Naming Convention
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

### Making Changes
1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes following our coding standards**
3. **Add or update tests for your changes**
4. **Run the test suite:**
```bash
make test
```

5. **Format your code:**
```bash
make format
```

6. **Commit your changes:**
```bash
git commit -m "feat: add your feature description"
```

### Commit Message Convention
We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api.py -v

# Run tests with output
pytest -s
```

### Writing Tests
- Add tests for all new functionality
- Maintain comprehensive test coverage above industry standards
- Use descriptive test names
- Follow the existing test patterns

### Test Structure
```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_api.py          # API endpoint tests
├── test_models.py       # Data model tests
├── test_processor.py    # Log processing tests
└── test_file_upload.py  # File upload tests
```

## 📝 Code Style

### Python Code Style
- Follow [PEP 8](https://pep8.org/)
- Use type hints where appropriate
- Maintain docstring coverage for functions and classes
- Use meaningful variable and function names

### Code Formatting
We use automated code formatting:
```bash
# Format code
black app/ tests/

# Check formatting
black --check app/ tests/

# Lint code
flake8 app/ tests/
```

### Frontend Code Style
- Use consistent indentation (2 spaces for HTML/CSS/JS)
- Follow semantic HTML practices
- Use CSS custom properties for theming
- Write clean, readable JavaScript

## 📚 Documentation

### API Documentation
- API documentation is auto-generated from code comments
- Update docstrings when changing API behavior
- Test your changes against the generated docs at `/docs`

### README Updates
- Update README.md if adding new features
- Include usage examples for new functionality
- Update configuration sections if adding new settings

## 🐛 Bug Reports

### Before Reporting
1. Search existing issues to avoid duplicates
2. Test with the latest version
3. Try to reproduce the issue with minimal code

### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.11.0]
- Debuggle version: [e.g. 1.0.0]
```

## ✨ Feature Requests

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions you've considered.

**Additional context**
Any other context or screenshots.
```

## 🔍 Code Review Process

### Pull Request Guidelines
1. **Fill out the PR template completely**
2. **Reference related issues** using "Fixes #123" or "Closes #123"
3. **Add screenshots** for UI changes
4. **Ensure all tests pass**
5. **Keep PRs focused** - one feature per PR

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

## 🏷️ Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Workflow
1. Update CHANGELOG.md
2. Update version numbers
3. Create release PR
4. Tag release after merge
5. Deploy to production

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Celebrate diversity of thought and experience

### Getting Help
- **GitHub Discussions** - General questions and ideas
- **GitHub Issues** - Bug reports and feature requests
- **Documentation** - Check `/docs` endpoint when running locally

## 📄 License

By contributing to Debuggle Core, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Debuggle Core! 🎉