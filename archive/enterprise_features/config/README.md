# Configuration Templates

This directory contains configuration templates and examples for different deployment scenarios.

## 📁 Files

- `docker-compose.prod.yml` - Production Docker Compose configuration
- `nginx.conf` - Nginx reverse proxy configuration  
- `gunicorn.conf.py` - Gunicorn WSGI server configuration
- `supervisord.conf` - Process management configuration
- `logging.conf` - Logging configuration template

## 🚀 Usage

Copy and customize these templates for your deployment:

```bash
# Production deployment
cp config/docker-compose.prod.yml docker-compose.override.yml

# Nginx setup  
cp config/nginx.conf /etc/nginx/sites-available/debuggle

# Custom logging
cp config/logging.conf app/logging.conf
```

## 🔧 Environment Variables

See `.env.example` in the root directory for all available environment variables.