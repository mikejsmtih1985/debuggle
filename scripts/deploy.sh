#!/bin/bash

# Production deployment script for Debuggle
# This script handles production deployment with Docker

set -e

echo "🚀 Deploying Debuggle to production..."

# Configuration
IMAGE_NAME="debuggle"
CONTAINER_NAME="debuggle-app"
PORT="${PORT:-8000}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Stop existing container if running
if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
    echo "🛑 Stopping existing container..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Build new image
echo "🔨 Building Docker image..."
docker build -t $IMAGE_NAME:latest .

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads logs ssl-certs

# Set permissions
chmod 755 uploads logs

# Deploy with Docker Compose
if [ -f "docker-compose.yml" ]; then
    echo "🐳 Deploying with Docker Compose..."
    
    # Use production override if available
    if [ -f "config/docker-compose.prod.yml" ]; then
        docker-compose -f docker-compose.yml -f config/docker-compose.prod.yml up -d
    else
        docker-compose up -d
    fi
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    # Health check
    echo "🏥 Performing health check..."
    if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
        echo "✅ Service is healthy and running!"
    else
        echo "❌ Health check failed. Check logs with: docker-compose logs"
        exit 1
    fi
    
else
    # Deploy single container
    echo "🐳 Deploying single container..."
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:8000 \
        -v $(pwd)/uploads:/app/uploads \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/.env:/app/.env \
        --restart unless-stopped \
        --health-cmd="curl -f http://localhost:8000/health || exit 1" \
        --health-interval=30s \
        --health-timeout=10s \
        --health-retries=3 \
        $IMAGE_NAME:latest
    
    # Wait for container to be ready
    echo "⏳ Waiting for container to be ready..."
    sleep 10
    
    # Health check
    echo "🏥 Performing health check..."
    if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
        echo "✅ Service is healthy and running!"
    else
        echo "❌ Health check failed. Check logs with: docker logs $CONTAINER_NAME"
        exit 1
    fi
fi

echo ""
echo "🎉 Deployment successful!"
echo ""
echo "📊 Service Status:"
if command -v docker-compose > /dev/null 2>&1 && [ -f "docker-compose.yml" ]; then
    docker-compose ps
else
    docker ps -f name=$CONTAINER_NAME
fi

echo ""
echo "🌐 Service URLs:"
echo "  - Health Check: http://localhost:$PORT/health"
echo "  - Web Interface: http://localhost:$PORT"
echo "  - API Documentation: http://localhost:$PORT/docs"
echo ""
echo "📝 Useful commands:"
echo "  - View logs: docker-compose logs -f (or docker logs $CONTAINER_NAME -f)"
echo "  - Stop service: docker-compose down (or docker stop $CONTAINER_NAME)"
echo "  - Update service: $0"
echo ""