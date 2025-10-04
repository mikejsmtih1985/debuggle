# Docker Deployment Guide

This guide covers deploying Debuggle using Docker containers for development, testing, and production environments.

## 🐳 Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ installed  
- At least 2GB RAM available
- Port 8000 available (or configure different port)

## 🚀 Quick Start with Docker Compose

### 1. Clone and Setup

```bash
git clone https://github.com/mikejsmtih1985/debuggle.git
cd debuggle
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your settings:

```env
# Application Settings
APP_NAME=Debuggle Core
APP_VERSION=1.0.0
DEBUG=false

# Server Configuration  
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Security
SECRET_KEY=your-secret-key-here
API_KEY_HEADER=X-API-Key

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/app/uploads
```

### 3. Build and Run

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 4. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# Process a test log
curl -X POST http://localhost:8000/debuggle-log \
  -H "Content-Type: application/json" \
  -d '{"content": "Test log entry", "tier": "core"}'
```

## 🏗️ Production Deployment

### Docker Compose Override

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  debuggle:
    build:
      context: .
      target: production
    environment:
      - DEBUG=false
      - WORKERS=8
    restart: unless-stopped
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    ports:
      - "80:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl-certs:/etc/nginx/ssl:ro
    depends_on:
      - debuggle
    restart: unless-stopped
```

### Production Startup

```bash
# Deploy to production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale application instances
docker-compose up -d --scale debuggle=3
```

## 🔧 Single Container Deployment

### Build Custom Image

```bash
# Build the image
docker build -t debuggle:latest .

# Run container
docker run -d \
  --name debuggle-app \
  -p 8000:8000 \
  -e DEBUG=false \
  -e WORKERS=4 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/.env:/app/.env \
  debuggle:latest
```

### Using Pre-built Image

```bash
# Pull from registry (when available)
docker pull debuggle/core:latest

# Run with minimal config
docker run -d \
  --name debuggle \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  debuggle/core:latest
```

## 🔄 Container Management

### Useful Commands

```bash
# View running containers
docker ps

# Check application logs
docker logs debuggle-app -f

# Execute commands in container
docker exec -it debuggle-app bash

# Update container
docker pull debuggle:latest
docker stop debuggle-app
docker rm debuggle-app
docker run -d --name debuggle-app ... debuggle:latest

# Backup uploads directory
docker exec debuggle-app tar czf /tmp/uploads-backup.tar.gz /app/uploads
docker cp debuggle-app:/tmp/uploads-backup.tar.gz ./backup/
```

### Health Monitoring

```bash
# Health check script
#!/bin/bash
if curl -f http://localhost:8000/health; then
    echo "✅ Service is healthy"
    exit 0
else  
    echo "❌ Service is unhealthy"
    exit 1
fi

# Auto-restart on failure
docker run -d \
  --name debuggle \
  --restart=unless-stopped \
  --health-cmd="curl -f http://localhost:8000/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  debuggle:latest
```

## 🌐 Reverse Proxy Setup

### Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream debuggle {
        server debuggle:8000;
    }
    
    server {
        listen 80;
        server_name your-domain.com;
        
        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name your-domain.com;
        
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        
        # File upload size
        client_max_body_size 10M;
        
        location / {
            proxy_pass http://debuggle;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }
}
```

### Traefik Configuration

Add labels to `docker-compose.yml`:

```yaml
services:
  debuggle:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.debuggle.rule=Host(`your-domain.com`)"
      - "traefik.http.routers.debuggle.tls=true"
      - "traefik.http.routers.debuggle.tls.certresolver=letsencrypt"
      - "traefik.http.services.debuggle.loadbalancer.server.port=8000"
```

## 📊 Monitoring and Logging

### Log Configuration

```yaml
# In docker-compose.yml
services:
  debuggle:
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "5"
        labels: "service=debuggle"
```

### Metrics Collection

```bash
# View container stats
docker stats debuggle-app

# Export metrics
docker exec debuggle-app curl http://localhost:8000/metrics
```

## 🔐 Security Best Practices

### Container Security

```dockerfile
# In Dockerfile - already implemented
FROM python:3.12-slim as base

# Create non-root user
RUN adduser --disabled-password --gecos '' --uid 1000 debuggle
USER debuggle

# Use read-only root filesystem
# docker run --read-only -v /tmp --tmpfs /tmp debuggle:latest
```

### Environment Security

```bash
# Use Docker secrets for sensitive data
echo "your-secret-key" | docker secret create debuggle_secret_key -

# Reference in compose
services:
  debuggle:
    secrets:
      - debuggle_secret_key
    environment:
      - SECRET_KEY_FILE=/run/secrets/debuggle_secret_key

secrets:
  debuggle_secret_key:
    external: true
```

## 🚀 Scaling and Performance

### Horizontal Scaling

```bash
# Scale application instances
docker-compose up -d --scale debuggle=5

# Use load balancer
# Update nginx upstream block with multiple servers
upstream debuggle {
    server debuggle_1:8000;
    server debuggle_2:8000;  
    server debuggle_3:8000;
}
```

### Resource Limits

```yaml
# In docker-compose.yml
services:
  debuggle:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

## 🆘 Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker logs debuggle-app

# Check configuration
docker exec debuggle-app env | grep -E "(DEBUG|PORT|HOST)"
```

**Port conflicts:**
```bash
# Find what's using port 8000
sudo netstat -tulpn | grep :8000

# Use different port
docker run -p 8080:8000 debuggle:latest
```

**File permission issues:**
```bash
# Fix upload directory permissions
sudo chown -R 1000:1000 ./uploads
```

## 📚 Next Steps

- [Kubernetes Deployment](./kubernetes.md)
- [Cloud Deployment](./cloud.md)
- [Monitoring Setup](./monitoring.md)
- [Performance Tuning](./performance.md)