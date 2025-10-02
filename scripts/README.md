# Scripts Directory

This directory contains utility scripts for development, deployment, and maintenance of Debuggle.

## 📁 Available Scripts

### 🔧 Development Scripts

#### `setup-dev.sh`
Sets up the development environment with all dependencies.

```bash
./scripts/setup-dev.sh
```

**What it does:**
- Creates Python virtual environment
- Installs all dependencies from requirements.txt
- Creates .env file from template
- Sets up necessary directories
- Validates installation

#### `test.sh`
Runs comprehensive test suite including unit tests, integration tests, and performance checks.

```bash
./scripts/test.sh
```

**What it does:**
- Runs pytest unit tests
- Performs integration tests against running service
- Checks code style with flake8
- Runs security analysis with bandit
- Performs basic performance testing

### 🚀 Deployment Scripts

#### `deploy.sh`
Handles production deployment using Docker.

```bash
./scripts/deploy.sh
```

**What it does:**
- Builds Docker image
- Stops existing containers
- Deploys with Docker Compose or single container
- Performs health checks
- Shows deployment status

**Environment Variables:**
- `PORT`: Port to expose (default: 8000)
- `IMAGE_NAME`: Docker image name (default: debuggle)
- `CONTAINER_NAME`: Container name (default: debuggle-app)

### 🛠️ Maintenance Scripts

#### `backup.sh`
Creates comprehensive backups of application data and configuration.

```bash
./scripts/backup.sh
```

**What it does:**
- Creates compressed backup of application code
- Backs up configuration files
- Archives uploaded files
- Archives log files
- Cleans up old backups (keeps last 10)

**Environment Variables:**
- `BACKUP_DIR`: Backup directory (default: ./backups)

## 🎯 Usage Examples

### Complete Development Setup
```bash
# Clone and setup
git clone https://github.com/mikejsmtih1985/debuggle.git
cd debuggle
./scripts/setup-dev.sh

# Run tests
./scripts/test.sh

# Start development server
source venv/bin/activate
uvicorn app.main:app --reload
```

### Production Deployment
```bash
# Deploy to production
./scripts/deploy.sh

# Create backup before updates
./scripts/backup.sh

# Update deployment
git pull origin main
./scripts/deploy.sh
```

### Continuous Integration
```bash
# CI pipeline example
./scripts/setup-dev.sh
./scripts/test.sh
if [ $? -eq 0 ]; then
    ./scripts/deploy.sh
fi
```

## 🔧 Customization

### Adding New Scripts

1. Create your script in the `scripts/` directory
2. Make it executable: `chmod +x scripts/your-script.sh`
3. Follow the naming convention: `action-description.sh`
4. Add proper error handling with `set -e`
5. Include helpful output messages
6. Update this README

### Script Template

```bash
#!/bin/bash

# Description of what this script does
# Usage: ./scripts/your-script.sh [options]

set -e

echo "🚀 Starting your script..."

# Configuration
VARIABLE="${VARIABLE:-default_value}"

# Your script logic here

echo "✅ Script completed successfully!"
```

## 📋 Requirements

These scripts require the following tools to be installed:

- **bash** - Shell scripting
- **curl** - HTTP requests and health checks
- **docker** - Container deployment
- **docker-compose** - Multi-container deployment
- **python3** - Python development
- **tar** - Archive creation
- **jq** - JSON processing (optional, for security checks)
- **bc** - Basic calculator (for performance tests)

## 🆘 Troubleshooting

### Permission Errors
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Docker Not Running
```bash
# Start Docker service
sudo systemctl start docker

# Or on macOS
open -a Docker
```

### Virtual Environment Issues
```bash
# Remove and recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Network Issues
```bash
# Check if port is available
netstat -tulpn | grep :8000

# Kill process using port
sudo lsof -t -i:8000 | xargs kill
```

## 🔗 Related Documentation

- [Getting Started Guide](../docs/user-guide/getting-started.md)
- [Docker Deployment](../docs/deployment/docker.md)
- [API Documentation](../docs/api/README.md)
- [Contributing Guidelines](../CONTRIBUTING.md)