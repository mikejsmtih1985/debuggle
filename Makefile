# Start the development server
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# Format code
format:
	black app/ tests/
	
# Lint code
lint:
	flake8 app/ tests/

# Build Docker image
build:
	docker build -t debuggle-trace:latest .

# Run with Docker Compose
up:
	docker-compose up --build

# Stop Docker Compose
down:
	docker-compose down

# Clean up Docker
clean:
	docker-compose down -v
	docker image prune -f

# Deploy to production (example)
deploy:
	docker build -t debuggle-trace:$(shell git rev-parse --short HEAD) .
	# Add your deployment commands here

.PHONY: dev install test test-cov format lint build up down clean deploy