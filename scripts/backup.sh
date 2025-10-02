#!/bin/bash

# Backup script for Debuggle
# Creates backups of important data and configuration

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="debuggle_backup_$TIMESTAMP"

echo "💾 Creating Debuggle backup..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup archive
echo "📦 Creating backup archive: $BACKUP_NAME.tar.gz"

tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
    --exclude=venv \
    --exclude=.venv \
    --exclude=__pycache__ \
    --exclude=*.pyc \
    --exclude=.git \
    --exclude=.pytest_cache \
    --exclude=node_modules \
    --exclude=backups \
    . 2>/dev/null

# Create database backup if applicable
# (Add database backup commands here when needed)

# Create configuration backup
echo "⚙️  Backing up configuration..."
mkdir -p "$BACKUP_DIR/configs_$TIMESTAMP"
cp .env* "$BACKUP_DIR/configs_$TIMESTAMP/" 2>/dev/null || true
cp docker-compose*.yml "$BACKUP_DIR/configs_$TIMESTAMP/" 2>/dev/null || true
cp config/* "$BACKUP_DIR/configs_$TIMESTAMP/" 2>/dev/null || true

# Create uploads backup if directory exists
if [ -d "uploads" ] && [ "$(ls -A uploads 2>/dev/null)" ]; then
    echo "📁 Backing up uploaded files..."
    tar -czf "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" uploads/
fi

# Create logs backup if directory exists
if [ -d "logs" ] && [ "$(ls -A logs 2>/dev/null)" ]; then
    echo "📋 Backing up logs..."
    tar -czf "$BACKUP_DIR/logs_$TIMESTAMP.tar.gz" logs/
fi

# Get backup size
backup_size=$(du -h "$BACKUP_DIR/$BACKUP_NAME.tar.gz" | cut -f1)

echo ""
echo "✅ Backup completed successfully!"
echo ""
echo "📊 Backup Details:"
echo "  📦 Main backup: $BACKUP_DIR/$BACKUP_NAME.tar.gz ($backup_size)"
echo "  ⚙️  Configs: $BACKUP_DIR/configs_$TIMESTAMP/"
if [ -f "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" ]; then
    uploads_size=$(du -h "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" | cut -f1)
    echo "  📁 Uploads: $BACKUP_DIR/uploads_$TIMESTAMP.tar.gz ($uploads_size)"
fi
if [ -f "$BACKUP_DIR/logs_$TIMESTAMP.tar.gz" ]; then
    logs_size=$(du -h "$BACKUP_DIR/logs_$TIMESTAMP.tar.gz" | cut -f1)
    echo "  📋 Logs: $BACKUP_DIR/logs_$TIMESTAMP.tar.gz ($logs_size)"
fi
echo ""
echo "🔄 To restore from backup:"
echo "  1. Extract: tar -xzf $BACKUP_DIR/$BACKUP_NAME.tar.gz"
echo "  2. Restore configs: cp configs_$TIMESTAMP/* ."
echo "  3. Restore uploads: tar -xzf uploads_$TIMESTAMP.tar.gz"
echo "  4. Run setup: ./scripts/setup-dev.sh"
echo ""

# Optional: Clean up old backups (keep last 10)
echo "🧹 Cleaning up old backups (keeping last 10)..."
cd "$BACKUP_DIR"
ls -t debuggle_backup_*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f || true
cd - > /dev/null

backup_count=$(ls -1 "$BACKUP_DIR"/debuggle_backup_*.tar.gz 2>/dev/null | wc -l)
echo "📊 Total backups: $backup_count"
echo ""