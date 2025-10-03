# 📚 Debuggle Data Persistence Guide - Everything You Need to Know

## 📖 Overview

This guide explains how Debuggle stores and manages your error data, designed for developers, team leads, and anyone who wants to understand how their debugging data is handled.

**TL;DR:** Debuggle uses SQLite to store all your error data locally in a single file. Your data stays on your machine, is lightning-fast to access, and costs nothing to maintain.

## 🎯 For Busy Developers (2-Minute Read)

### The Essentials
- **Where:** Single SQLite file (default: `logs.db` in your project directory)
- **Privacy:** 100% local - your error data never leaves your machine
- **Performance:** Sub-second search across millions of error records
- **Cost:** $0 - no cloud databases or monthly bills
- **Backup:** Just copy the database file (that's it!)

### Quick Actions
```bash
# Find your database
ls -la logs.db                           # Default location

# Backup your data  
cp logs.db logs_backup_$(date +%Y%m%d).db

# Check database size
du -h logs.db

# Quick statistics
sqlite3 logs.db "SELECT COUNT(*) as total_logs FROM logs;"
```

---

## 🗄️ How Your Data is Stored

### The Database File

Debuggle creates a single SQLite database file that contains all your error logs:

```
your-project/
├── logs.db              ← All your error data is here
├── your_app.py
└── other_files...
```

**Key Points:**
- **One file contains everything** - logs, search indexes, statistics
- **Human-readable** - Standard SQLite format, viewable with any SQLite tool
- **Portable** - Move between machines by copying this file
- **Self-contained** - No external dependencies or connections needed

### What Gets Stored

Every error that Debuggle analyzes is stored with:

| **Field** | **What It Contains** | **Example** |
|-----------|---------------------|-------------|
| **Original Error** | Raw error message as it appeared | `IndexError: list index out of range` |
| **Enhanced Analysis** | Debuggle's formatted explanation | `🚨 [PYTHON] Array bounds error - tried to access index 999` |
| **Context** | When, where, what language | `2025-01-15 14:30:22, Python, app.py line 42` |
| **Classification** | Error type, severity, tags | `["indexerror", "python", "logic-error"]` |
| **Project Info** | Which project/app this belongs to | `my-web-app` |

## 📊 Data Retention Policies

### Free Tier (Default)
- **Retention:** 7 days of error history
- **Storage:** Unlimited errors within the retention period
- **Cleanup:** Automatic removal of errors older than 7 days

### Pro Tier
- **Retention:** 90 days of error history  
- **Advanced analytics:** Trend analysis and pattern recognition
- **Custom retention:** Configure retention periods per project

### Enterprise Tier
- **Retention:** 1 year+ with custom policies
- **Compliance features:** Audit trails, export capabilities
- **Archive support:** Long-term storage with compression

### Manual Retention Control
```bash
# See current retention settings
python -c "from debuggle.storage import RetentionManager, DatabaseManager; 
rm = RetentionManager(DatabaseManager()); print(rm.get_current_policy())"

# Clean up old logs manually
python -c "from debuggle.storage import DatabaseManager; 
db = DatabaseManager(); print(f'Deleted {db.delete_logs_older_than(30)} logs older than 30 days')"
```

## 💾 Backup and Recovery

### Simple Backups (Recommended)

**Daily Backup Script:**
```bash
#!/bin/bash
# backup_debuggle.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp logs.db "backups/logs_backup_$DATE.db"
echo "Backup created: logs_backup_$DATE.db"

# Keep only last 30 days of backups
find backups/ -name "logs_backup_*.db" -mtime +30 -delete
```

**One-Time Backup:**
```bash
# Quick backup
cp logs.db logs_backup.db

# Backup with timestamp
cp logs.db "logs_backup_$(date +%Y%m%d).db"
```

### Advanced Backups

**Hot Backup (while Debuggle is running):**
```bash
# SQLite-safe backup that works even while database is in use
sqlite3 logs.db ".backup logs_hot_backup.db"
```

**Compressed Backup:**
```bash
# Create compressed backup
tar -czf "logs_backup_$(date +%Y%m%d).tar.gz" logs.db

# Restore from compressed backup
tar -xzf logs_backup_20250115.tar.gz
```

### Recovery

**Simple Recovery:**
```bash
# Replace current database with backup
cp logs_backup.db logs.db

# Verify recovery worked
sqlite3 logs.db "SELECT COUNT(*) FROM logs;"
```

**Merge Backups:**
```bash
# If you have multiple database files to combine
sqlite3 main_logs.db ".read merge_script.sql"
```

## 🔍 Finding and Managing Your Data

### Database Location

**Default Location:**
- Current working directory: `./logs.db`
- When using Debuggle server: Same directory as the server

**Custom Location:**
```bash
# Set custom path via environment variable
export DEBUGGLE_DB_PATH="/path/to/my/custom/logs.db"

# Or specify in code
from debuggle.storage import DatabaseManager
db = DatabaseManager("/path/to/my/logs.db")
```

### Database Information
```bash
# Check database size and record count
sqlite3 logs.db "
SELECT 
    COUNT(*) as total_logs,
    MIN(timestamp) as oldest_log,
    MAX(timestamp) as newest_log,
    COUNT(DISTINCT language) as languages_seen,
    COUNT(DISTINCT project_name) as projects
FROM logs;"

# Storage statistics
sqlite3 logs.db "
SELECT 
    page_count * page_size / 1024 / 1024 as size_mb,
    page_count as total_pages,
    freelist_count as free_pages
FROM pragma_page_count(), pragma_page_size(), pragma_freelist_count();"
```

## 🔧 Database Maintenance

### Automatic Maintenance

Debuggle automatically handles:
- **Index optimization** - Keeps searches fast as data grows
- **Space reclamation** - Removes deleted data to prevent bloat
- **Query optimization** - Updates statistics for better performance

### Manual Maintenance

**Optimize Database Performance:**
```bash
# Reclaim deleted space and optimize
sqlite3 logs.db "VACUUM;"

# Update query optimizer statistics  
sqlite3 logs.db "ANALYZE;"

# Check database integrity
sqlite3 logs.db "PRAGMA integrity_check;"
```

**Monthly Maintenance Script:**
```bash
#!/bin/bash
# monthly_maintenance.sh
echo "Starting database maintenance..."

# Backup before maintenance
cp logs.db logs_pre_maintenance.db

# Optimize database
sqlite3 logs.db "VACUUM; ANALYZE;"

# Check integrity
INTEGRITY=$(sqlite3 logs.db "PRAGMA integrity_check;")
if [ "$INTEGRITY" = "ok" ]; then
    echo "✅ Database maintenance completed successfully"
    rm logs_pre_maintenance.db  # Remove backup
else
    echo "❌ Database integrity issues found: $INTEGRITY"
    echo "Restored from backup"
    mv logs_pre_maintenance.db logs.db
fi
```

## 📈 Monitoring Database Health

### Built-in Health Checks

```python
from debuggle.storage import DatabaseManager

db = DatabaseManager()

# Get database statistics
stats = db.get_statistics()
print(f"Total logs: {stats.total_logs}")
print(f"Database size: {stats.database_size_mb} MB")
print(f"Oldest log: {stats.oldest_log}")
print(f"Error rate trend: {stats.error_rate_trend}")

# Performance metrics
health = db.get_health_metrics()
print(f"Average query time: {health.avg_query_time_ms} ms")
print(f"Index hit ratio: {health.index_hit_ratio}%")
```

### Manual Health Checks

```bash
# Check database statistics
sqlite3 logs.db "
SELECT 
    'Total Logs' as metric, COUNT(*) as value FROM logs
UNION ALL
SELECT 
    'Last 24h Errors', COUNT(*) FROM logs 
    WHERE timestamp >= datetime('now', '-1 day') AND severity IN ('error', 'critical')
UNION ALL
SELECT 
    'Unique Projects', COUNT(DISTINCT project_name) FROM logs
UNION ALL  
SELECT 
    'Languages Seen', COUNT(DISTINCT language) FROM logs;"

# Performance analysis
sqlite3 logs.db "EXPLAIN QUERY PLAN 
SELECT * FROM logs WHERE timestamp >= datetime('now', '-1 day') ORDER BY timestamp DESC;"
```

## 🔒 Security and Privacy

### Data Protection

**Local Storage Benefits:**
- ✅ **No network transmission** - Data never sent to external servers
- ✅ **File system security** - Protected by your OS permissions
- ✅ **No API keys or tokens** - No external service credentials to manage
- ✅ **Corporate firewall friendly** - No outbound connections required

**File Permissions:**
```bash
# Secure the database file (owner read/write only)
chmod 600 logs.db

# Check current permissions
ls -la logs.db
```

### Encryption Options

**File-Level Encryption:**
```bash
# Encrypt database file with gpg
gpg --symmetric --cipher-algo AES256 logs.db

# Decrypt when needed
gpg --decrypt logs.db.gpg > logs.db
```

**SQLite Encryption Extensions:**
```python
# For enterprise environments requiring database encryption
# Note: Requires SQLCipher extension
import sqlite3
import sqlite3_encryption  # Third-party extension

conn = sqlite3.connect('encrypted_logs.db')
conn.execute("PRAGMA key = 'your-encryption-key'")
```

## 🚀 Advanced Usage

### Multiple Projects

**Separate Databases per Project:**
```bash
# Organize by project
project1/logs.db
project2/logs.db
shared_services/logs.db
```

**Single Database with Project Separation:**
```python
# All projects in one database, filtered by project_name
db = DatabaseManager("all_projects.db")
web_app_errors = db.search_logs(project_name="web-app")
api_errors = db.search_logs(project_name="api-service")
```

### Data Export

**Export to JSON:**
```bash
sqlite3 logs.db "
SELECT json_object(
    'log_id', log_id,
    'timestamp', timestamp,
    'original_log', original_log,
    'severity', severity,
    'language', language,
    'project_name', project_name
) FROM logs 
WHERE timestamp >= datetime('now', '-1 day');" > recent_errors.json
```

**Export to CSV:**
```bash
sqlite3 -header -csv logs.db "
SELECT timestamp, severity, language, summary, project_name 
FROM logs 
WHERE timestamp >= datetime('now', '-7 days');" > weekly_errors.csv
```

### Integration with External Tools

**Logging Integration:**
```python
import logging
from debuggle.storage import DatabaseManager

# Custom log handler that stores in Debuggle
class DebuggleHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
    
    def emit(self, record):
        # Store log records directly in Debuggle database
        pass
```

## 🆘 Troubleshooting

### Common Issues

**Database Locked Error:**
```bash
# Check if another process is using the database
lsof logs.db

# Kill blocking processes (be careful!)
pkill -f "debuggle"

# Or wait for processes to finish
```

**Database Corruption:**
```bash
# Check database integrity
sqlite3 logs.db "PRAGMA integrity_check;"

# Repair minor corruption
sqlite3 logs.db "REINDEX;"

# Restore from backup if needed
cp logs_backup.db logs.db
```

**Performance Issues:**
```bash
# Check if database needs optimization
sqlite3 logs.db "PRAGMA optimize;"

# Force full optimization
sqlite3 logs.db "VACUUM; ANALYZE;"

# Check for missing indexes
sqlite3 logs.db ".schema logs"
```

### Getting Help

**Debug Mode:**
```python
import logging
logging.getLogger('debuggle.storage').setLevel(logging.DEBUG)

# Now all database operations will be logged
```

**Database Analysis:**
```bash
# Generate comprehensive database report
sqlite3 logs.db "
.headers on
.mode column  
SELECT 'Table Info' as section;
.schema logs
SELECT 'Index Info' as section;
.indices logs
SELECT 'Statistics' as section;
SELECT COUNT(*) as total_logs, 
       COUNT(DISTINCT severity) as severity_levels,
       COUNT(DISTINCT language) as languages
FROM logs;"
```

---

## 📚 Additional Resources

- **[Technical Implementation Details](SQLITE_IMPLEMENTATION.md)** - Deep dive into architecture
- **[Database Schema Reference](DATABASE_SCHEMA.md)** - Complete field documentation
- **[Performance Optimization Guide](docs/PERFORMANCE_TUNING.md)** - Advanced tuning tips
- **[Migration Guide](docs/MIGRATION_GUIDE.md)** - Moving between versions

---

*Your error data is valuable. Debuggle's SQLite implementation ensures it stays safe, private, and accessible - exactly where it belongs.*