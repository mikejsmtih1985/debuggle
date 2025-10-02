# Start the development server
# Development server
dev:
	uvicorn src.debuggle.main:app --reload --host 0.0.0.0 --port 8000

# Install dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

# Install in editable mode
install-local:
	pip install -e .

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest --cov=src/debuggle --cov-report=html --cov-report=term-missing

# Format code
format:
	black src/ tests/ cli/ examples/
	
# Lint code
lint:
	flake8 src/ tests/ cli/ examples/
	mypy src/

# Type checking
typecheck:
	mypy src/debuggle

# CLI tool
cli:
	python cli/debuggle_cli.py

# Run examples
examples:
	cd examples && python demo_errors.py

# Build package
build:
	python -m build

# Build Docker image
docker-build:
	cd docker && docker build -t debuggle-core:latest -f Dockerfile ..

# Run with Docker Compose
docker-up:
	cd docker && docker-compose up --build

# Stop Docker Compose
docker-down:
	cd docker && docker-compose down

# Clean up Docker
docker-clean:
	cd docker && docker-compose down -v
	docker image prune -f

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Setup development environment
setup:
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
	.venv/bin/pip install -e .
	.venv/bin/pre-commit install

# Check project structure
check:
	python -c "import src.debuggle; print('✅ Import successful')"
	python cli/debuggle_cli.py --help
	pytest --collect-only

.PHONY: dev install install-dev install-local test test-cov format lint typecheck cli examples build docker-build docker-up docker-down docker-clean clean setup check

# Help command
help:
	@echo "Available commands:"
	@echo "  dev      - Start development server"
	@echo "  install  - Install Python dependencies"
	@echo "  test     - Run test suite"
	@echo "  test-cov - Run tests with coverage report"
	@echo "  format   - Format code with black"
	@echo "  lint     - Lint code with flake8"
	@echo "  build    - Build Docker image"
	@echo "  up       - Start with Docker Compose"
	@echo "  down     - Stop Docker Compose"
	@echo "  clean    - Clean up Docker resources"
	@echo "  deploy   - Deploy to production"
	@echo "  help     - Show this help message"

.PHONY: dev install test test-cov format lint build up down clean deploy