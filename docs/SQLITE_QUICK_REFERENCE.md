# 🗄️ Debuggle SQLite Quick Reference

## At a Glance

**Database Type:** SQLite (embedded, file-based)  
**Location:** `logs.db` in your project directory  
**Size:** ~1KB per log entry  
**Performance:** 10,000+ inserts/second, <10ms queries  
**Cost:** $0 (no cloud databases needed)  
**Backup:** Just copy the database file  

## 🚀 Key Benefits

✅ **Zero Configuration** - Works immediately after installation  
✅ **100% Private** - Your data never leaves your machine  
✅ **Lightning Fast** - No network latency, optimized indexes  
✅ **Cost Effective** - No monthly database bills or per-seat pricing  
✅ **Simple Backup** - Copy one file vs complex cloud procedures  
✅ **Production Ready** - Powers your phone, browser, and countless apps  

## 📊 Database Structure

```
logs.db
├── logs table          # Core error storage
│   ├── log_id         # Unique identifier
│   ├── timestamp      # When error occurred  
│   ├── original_log   # Raw error message
│   ├── processed_log  # Debuggle's analysis
│   ├── severity       # error, warning, critical, etc.
│   ├── language       # python, javascript, etc.
│   └── metadata       # JSON context data
├── search_fts         # Full-text search index
└── sqlite_stat*       # Query optimization data
```

## ⚡ Quick Commands

```bash
# Check database status
ls -la logs.db
du -h logs.db

# View log count
sqlite3 logs.db "SELECT COUNT(*) FROM logs;"

# Recent errors
sqlite3 logs.db "SELECT timestamp, severity, summary FROM logs ORDER BY timestamp DESC LIMIT 10;"

# Backup database
cp logs.db logs_backup_$(date +%Y%m%d).db

# Database maintenance
sqlite3 logs.db "VACUUM; ANALYZE;"
```

## 🔍 Common Queries

```sql
-- Recent critical errors
SELECT * FROM logs 
WHERE severity = 'critical' 
  AND timestamp >= datetime('now', '-24 hours');

-- Python errors by project
SELECT project_name, COUNT(*) as error_count
FROM logs 
WHERE language = 'python' 
GROUP BY project_name;

-- Search error content
SELECT * FROM logs 
WHERE original_log LIKE '%database connection%';

-- Error frequency by day
SELECT DATE(timestamp) as day, COUNT(*) as errors
FROM logs 
GROUP BY DATE(timestamp)
ORDER BY day DESC;
```

## 📈 Production Settings

```python
# Optimized SQLite configuration
PRAGMA journal_mode = WAL;     # Better concurrency
PRAGMA synchronous = NORMAL;   # Balanced safety/speed  
PRAGMA cache_size = 10000;     # 10MB cache
PRAGMA temp_store = MEMORY;    # Temp tables in RAM
```

## 🔒 Security & Privacy

- **Local Storage Only** - No external data transmission
- **File System Permissions** - Standard OS-level security
- **No API Keys** - No external service credentials to manage
- **GDPR Compliant** - Easy data deletion and export
- **Corporate Safe** - No firewall or compliance issues

## 📚 Full Documentation

- **[Complete Implementation Guide](SQLITE_IMPLEMENTATION.md)** - Architecture deep dive
- **[Database Schema Reference](DATABASE_SCHEMA.md)** - Field specifications  
- **[User Guide](DATA_PERSISTENCE_GUIDE.md)** - Backup, maintenance, troubleshooting
- **[Admin Guide](DATABASE_ADMINISTRATION.md)** - Production optimization

---

*"Professional-grade data persistence without the enterprise complexity"*