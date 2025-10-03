# 🔧 Debuggle Database Administration Guide

## 📖 Overview

This guide provides comprehensive technical documentation for database administrators, DevOps engineers, and senior developers who need to manage, optimize, and troubleshoot Debuggle's SQLite implementation in production environments.

## 🎯 Target Audience

- **Database Administrators** - Managing Debuggle in production
- **DevOps Engineers** - Deployment and monitoring
- **Senior Developers** - Performance optimization and troubleshooting
- **System Architects** - Integration planning and capacity planning

---

## 🏗️ Architecture Deep Dive

### SQLite Engine Configuration

Debuggle uses SQLite with specific optimizations for log storage workloads:

```python
# Production-optimized SQLite configuration
PRAGMA journal_mode = WAL;           # Write-Ahead Logging for concurrency
PRAGMA synchronous = NORMAL;         # Balance between safety and speed
PRAGMA cache_size = 10000;          # 10MB cache (adjust based on RAM)
PRAGMA temp_store = MEMORY;          # Temporary tables in RAM
PRAGMA mmap_size = 268435456;        # 256MB memory-mapped I/O
PRAGMA optimize;                     # Automatic optimization
```

### Connection Pool Management

```python
import sqlite3
import threading
from contextlib import contextmanager

class ConnectionPool:
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._connections = []
        self._lock = threading.Lock()
    
    @contextmanager
    def get_connection(self):
        conn = self._acquire_connection()
        try:
            yield conn
        finally:
            self._release_connection(conn)
    
    def _configure_connection(self, conn):
        """Apply production optimizations to new connections"""
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL") 
        conn.execute("PRAGMA cache_size = 10000")
        conn.execute("PRAGMA temp_store = MEMORY")
        return conn
```

## 📊 Performance Monitoring

### Built-in Performance Metrics

```python
from debuggle.storage import DatabaseManager
import time

class DatabaseMonitor:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
    def get_performance_metrics(self):
        """Comprehensive performance analysis"""
        with sqlite3.connect(self.db.database_path) as conn:
            # Query performance statistics
            stats = {}
            
            # Database size and page statistics
            stats['database_size_mb'] = conn.execute(
                "SELECT page_count * page_size / 1024.0 / 1024.0 FROM pragma_page_count(), pragma_page_size()"
            ).fetchone()[0]
            
            # Index usage statistics
            stats['index_usage'] = conn.execute("""
                SELECT name, stat FROM sqlite_stat1 
                WHERE tbl = 'logs' ORDER BY stat DESC
            """).fetchall()
            
            # Query plan analysis for common queries
            stats['query_plans'] = self._analyze_query_plans(conn)
            
            return stats
    
    def _analyze_query_plans(self, conn):
        """Analyze execution plans for critical queries"""
        plans = {}
        
        # Recent errors query
        plan = conn.execute("""
            EXPLAIN QUERY PLAN 
            SELECT * FROM logs 
            WHERE timestamp >= datetime('now', '-1 day') 
            ORDER BY timestamp DESC LIMIT 100
        """).fetchall()
        plans['recent_errors'] = plan
        
        # Severity filtering query  
        plan = conn.execute("""
            EXPLAIN QUERY PLAN
            SELECT * FROM logs 
            WHERE severity = 'error' AND timestamp >= datetime('now', '-1 day')
        """).fetchall()
        plans['severity_filter'] = plan
        
        return plans
```

### System Resource Monitoring

```bash
#!/bin/bash
# database_monitor.sh - Production monitoring script

DB_PATH="logs.db"
LOG_FILE="/var/log/debuggle/db_monitor.log"

# Database size monitoring
DB_SIZE=$(du -m "$DB_PATH" | cut -f1)
echo "$(date): Database size: ${DB_SIZE}MB" >> "$LOG_FILE"

# Connection monitoring
CONNECTIONS=$(lsof "$DB_PATH" | wc -l)
echo "$(date): Active connections: $CONNECTIONS" >> "$LOG_FILE"

# Performance check
QUERY_TIME=$(time sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM logs;" 2>&1 | grep real | cut -d' ' -f2)
echo "$(date): Query time: $QUERY_TIME" >> "$LOG_FILE"

# Disk space check
DISK_USAGE=$(df -h "$(dirname "$DB_PATH")" | tail -1 | awk '{print $5}')
echo "$(date): Disk usage: $DISK_USAGE" >> "$LOG_FILE"

# Alert if database is growing too fast
if [ "$DB_SIZE" -gt 1000 ]; then
    echo "WARNING: Database size exceeds 1GB" >> "$LOG_FILE"
    # Send alert (email, Slack, PagerDuty, etc.)
fi
```

## 🚀 Production Optimization

### Indexing Strategy

```sql
-- Core performance indexes (automatically created)
CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_severity ON logs(severity);  
CREATE INDEX IF NOT EXISTS idx_language ON logs(language);
CREATE INDEX IF NOT EXISTS idx_project ON logs(project_name);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_severity_timestamp ON logs(severity, timestamp);
CREATE INDEX IF NOT EXISTS idx_project_language ON logs(project_name, language);
CREATE INDEX IF NOT EXISTS idx_language_timestamp ON logs(language, timestamp);

-- Covering indexes for dashboard queries (Pro tier)
CREATE INDEX IF NOT EXISTS idx_dashboard_summary ON logs(
    timestamp, severity, language, project_name
) WHERE timestamp >= datetime('now', '-30 days');

-- Partial indexes for error analysis (Enterprise tier)
CREATE INDEX IF NOT EXISTS idx_errors_only ON logs(timestamp, project_name) 
WHERE severity IN ('error', 'critical');
```

### Query Optimization

```python
class OptimizedQueries:
    """Production-optimized query implementations"""
    
    @staticmethod
    def get_recent_errors_optimized(conn, hours=24, limit=100):
        """Optimized recent errors query with prepared statement"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Use prepared statement for better performance
        query = """
        SELECT log_id, timestamp, severity, summary, project_name
        FROM logs 
        WHERE timestamp >= ? 
          AND severity IN ('error', 'critical')
        ORDER BY timestamp DESC 
        LIMIT ?
        """
        
        return conn.execute(query, (cutoff_time, limit)).fetchall()
    
    @staticmethod
    def get_error_statistics_optimized(conn, days=7):
        """Optimized statistics query with single table scan"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = """
        SELECT 
            severity,
            language,
            project_name,
            COUNT(*) as error_count,
            MIN(timestamp) as first_seen,
            MAX(timestamp) as last_seen
        FROM logs 
        WHERE timestamp >= ?
        GROUP BY severity, language, project_name
        ORDER BY error_count DESC
        """
        
        return conn.execute(query, (cutoff_date,)).fetchall()
```

### Batch Processing Optimization

```python
class BatchProcessor:
    """Optimized batch operations for high-volume environments"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.batch_size = 1000
        
    def bulk_insert_logs(self, log_entries: List[LogEntry]):
        """Optimized bulk insert with transaction batching"""
        with sqlite3.connect(self.db.database_path) as conn:
            # Disable auto-commit for batch operations
            conn.execute("BEGIN TRANSACTION")
            
            try:
                # Prepare statement once, execute many times
                insert_sql = """
                INSERT OR REPLACE INTO logs (
                    log_id, timestamp, original_log, processed_log, 
                    summary, tags, severity, language, metadata, 
                    project_name, file_path, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                # Process in batches
                for i in range(0, len(log_entries), self.batch_size):
                    batch = log_entries[i:i + self.batch_size]
                    batch_data = [self._log_entry_to_tuple(log) for log in batch]
                    
                    conn.executemany(insert_sql, batch_data)
                    
                    # Intermediate commit for very large batches
                    if i > 0 and i % 10000 == 0:
                        conn.execute("COMMIT")
                        conn.execute("BEGIN TRANSACTION")
                
                conn.execute("COMMIT")
                return len(log_entries)
                
            except Exception as e:
                conn.execute("ROLLBACK")
                raise e
```

## 📈 Capacity Planning

### Storage Requirements

```python
def calculate_storage_requirements(
    daily_log_count: int,
    avg_log_size_bytes: int = 1024,
    retention_days: int = 90,
    growth_factor: float = 1.2
):
    """Calculate storage requirements for capacity planning"""
    
    # Base storage calculation
    daily_storage_mb = (daily_log_count * avg_log_size_bytes) / (1024 * 1024)
    total_storage_mb = daily_storage_mb * retention_days
    
    # Account for indexes (approximately 30% overhead)
    with_indexes_mb = total_storage_mb * 1.3
    
    # Apply growth factor
    projected_storage_mb = with_indexes_mb * growth_factor
    
    return {
        'daily_storage_mb': daily_storage_mb,
        'total_data_mb': total_storage_mb, 
        'with_indexes_mb': with_indexes_mb,
        'projected_storage_mb': projected_storage_mb,
        'projected_storage_gb': projected_storage_mb / 1024,
        'recommended_disk_gb': (projected_storage_mb / 1024) * 2  # 100% buffer
    }

# Example capacity planning
requirements = calculate_storage_requirements(
    daily_log_count=50000,      # 50K logs per day
    avg_log_size_bytes=1500,    # 1.5KB average log
    retention_days=90,          # 3-month retention
    growth_factor=1.5           # 50% growth buffer
)

print(f"Projected storage: {requirements['projected_storage_gb']:.1f} GB")
print(f"Recommended disk: {requirements['recommended_disk_gb']:.1f} GB")
```

### Performance Benchmarks

```python
import time
from concurrent.futures import ThreadPoolExecutor

class PerformanceBenchmark:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
    def benchmark_write_performance(self, num_logs=10000):
        """Benchmark write operations"""
        test_logs = self._generate_test_logs(num_logs)
        
        start_time = time.time()
        
        for log in test_logs:
            self.db.store_log(log)
            
        end_time = time.time()
        
        duration = end_time - start_time
        logs_per_second = num_logs / duration
        
        return {
            'total_logs': num_logs,
            'duration_seconds': duration,
            'logs_per_second': logs_per_second,
            'avg_latency_ms': (duration / num_logs) * 1000
        }
    
    def benchmark_read_performance(self, num_queries=1000):
        """Benchmark read operations"""
        start_time = time.time()
        
        for _ in range(num_queries):
            # Test common query patterns
            self.db.search_logs(
                start_date=datetime.now() - timedelta(days=1),
                limit=50
            )
            
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'total_queries': num_queries,
            'duration_seconds': duration,
            'queries_per_second': num_queries / duration,
            'avg_query_time_ms': (duration / num_queries) * 1000
        }
    
    def benchmark_concurrent_access(self, num_threads=10, operations_per_thread=100):
        """Benchmark concurrent database access"""
        def worker():
            results = []
            for _ in range(operations_per_thread):
                start = time.time()
                self.db.search_logs(limit=10)
                end = time.time()
                results.append(end - start)
            return results
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker) for _ in range(num_threads)]
            all_results = []
            for future in futures:
                all_results.extend(future.result())
        
        end_time = time.time()
        
        return {
            'total_operations': num_threads * operations_per_thread,
            'total_duration': end_time - start_time,
            'avg_latency_ms': (sum(all_results) / len(all_results)) * 1000,
            'operations_per_second': (num_threads * operations_per_thread) / (end_time - start_time)
        }
```

## 🔧 Maintenance Automation

### Automated Maintenance Scripts

```python
#!/usr/bin/env python3
"""
Automated database maintenance for production Debuggle deployments
"""

import sqlite3
import os
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path

class DatabaseMaintenance:
    def __init__(self, db_path: str, backup_dir: str = "./backups"):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('db_maintenance.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def daily_maintenance(self):
        """Daily maintenance routine"""
        self.logger.info("Starting daily maintenance routine")
        
        try:
            # Create backup
            backup_file = self.create_backup()
            self.logger.info(f"Backup created: {backup_file}")
            
            # Analyze database for query optimization
            self.analyze_database()
            
            # Check integrity
            if not self.check_integrity():
                self.logger.error("Database integrity check failed!")
                return False
            
            # Clean old backups (keep 30 days)
            self.cleanup_old_backups(days=30)
            
            self.logger.info("Daily maintenance completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Daily maintenance failed: {e}")
            return False
    
    def weekly_maintenance(self):
        """Weekly maintenance routine"""
        self.logger.info("Starting weekly maintenance routine")
        
        try:
            # Full backup before maintenance
            backup_file = self.create_backup(suffix="pre_weekly")
            
            # Vacuum database to reclaim space
            self.vacuum_database()
            
            # Update statistics for query optimizer
            self.update_statistics()
            
            # Rebuild indexes if needed
            self.rebuild_indexes_if_needed()
            
            # Generate maintenance report
            self.generate_maintenance_report()
            
            self.logger.info("Weekly maintenance completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Weekly maintenance failed: {e}")
            # Restore from backup if something went wrong
            self.restore_backup(backup_file)
            return False
    
    def create_backup(self, suffix="daily"):
        """Create timestamped database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"logs_backup_{suffix}_{timestamp}.db"
        backup_path = self.backup_dir / backup_filename
        
        with sqlite3.connect(self.db_path) as source:
            with sqlite3.connect(backup_path) as backup:
                source.backup(backup)
        
        return backup_path
    
    def vacuum_database(self):
        """Optimize database storage"""
        self.logger.info("Vacuuming database...")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("VACUUM")
            conn.commit()
        self.logger.info("Database vacuuming completed")
    
    def analyze_database(self):
        """Update query optimizer statistics"""
        self.logger.info("Analyzing database...")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("ANALYZE")
            conn.commit()
        self.logger.info("Database analysis completed")
    
    def check_integrity(self):
        """Verify database integrity"""
        self.logger.info("Checking database integrity...")
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("PRAGMA integrity_check").fetchone()[0]
            if result == "ok":
                self.logger.info("Database integrity check passed")
                return True
            else:
                self.logger.error(f"Database integrity check failed: {result}")
                return False
```

### Cron Job Configuration

```bash
# /etc/crontab - Production maintenance schedule

# Daily maintenance at 2 AM
0 2 * * * /usr/bin/python3 /path/to/debuggle/maintenance.py --daily

# Weekly maintenance on Sunday at 3 AM  
0 3 * * 0 /usr/bin/python3 /path/to/debuggle/maintenance.py --weekly

# Hourly health check
0 * * * * /path/to/debuggle/scripts/health_check.sh

# Daily backup verification
30 2 * * * /path/to/debuggle/scripts/verify_backup.sh
```

## 🚨 Monitoring and Alerting

### Health Check Endpoints

```python
from flask import Flask, jsonify
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/health/database')
def database_health():
    """Database health check endpoint for monitoring systems"""
    try:
        db_path = "logs.db"
        
        # Basic connectivity test
        with sqlite3.connect(db_path, timeout=5) as conn:
            conn.execute("SELECT 1")
            
        # Performance test
        start_time = time.time()
        with sqlite3.connect(db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
        query_time = (time.time() - start_time) * 1000
        
        # Size check
        db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
        
        # Recent activity check
        with sqlite3.connect(db_path) as conn:
            recent_logs = conn.execute("""
                SELECT COUNT(*) FROM logs 
                WHERE timestamp >= datetime('now', '-1 hour')
            """).fetchone()[0]
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'total_logs': count,
                'database_size_mb': round(db_size_mb, 2),
                'query_time_ms': round(query_time, 2),
                'recent_activity': recent_logs
            }
        }
        
        # Health thresholds
        if query_time > 1000:  # > 1 second
            health_status['status'] = 'degraded'
            health_status['warnings'] = ['High query latency']
            
        if db_size_mb > 10000:  # > 10GB
            health_status['status'] = 'warning'
            health_status['warnings'] = health_status.get('warnings', []) + ['Large database size']
        
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Define metrics
db_operations_total = Counter('debuggle_db_operations_total', 'Total database operations', ['operation'])
db_operation_duration = Histogram('debuggle_db_operation_duration_seconds', 'Database operation duration')
db_size_bytes = Gauge('debuggle_db_size_bytes', 'Database size in bytes')
db_connection_count = Gauge('debuggle_db_connections', 'Active database connections')

class MetricsCollector:
    def __init__(self, db_manager):
        self.db = db_manager
        
    def collect_metrics(self):
        """Collect and update Prometheus metrics"""
        try:
            # Database size
            db_size = os.path.getsize(self.db.database_path)
            db_size_bytes.set(db_size)
            
            # Connection count (approximate)
            connection_count = len([p for p in psutil.process_iter() 
                                  if 'sqlite' in p.name().lower()])
            db_connection_count.set(connection_count)
            
        except Exception as e:
            logging.error(f"Failed to collect metrics: {e}")
    
    def instrument_database_operation(self, operation_name):
        """Decorator to instrument database operations"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                db_operations_total.labels(operation=operation_name).inc()
                
                with db_operation_duration.time():
                    result = func(*args, **kwargs)
                
                return result
            return wrapper
        return decorator

# Start metrics server
start_http_server(8080)
```

## 🔒 Security Hardening

### File System Security

```bash
#!/bin/bash
# secure_database.sh - Database security hardening

DB_PATH="logs.db"
DB_DIR=$(dirname "$DB_PATH")
DB_USER="debuggle"
DB_GROUP="debuggle"

# Create dedicated user/group for database access
sudo useradd -r -s /bin/false "$DB_USER"
sudo groupadd "$DB_GROUP"

# Set secure file permissions
sudo chown "$DB_USER:$DB_GROUP" "$DB_PATH"
sudo chmod 640 "$DB_PATH"  # Read/write owner, read group, no access others

# Secure database directory
sudo chown "$DB_USER:$DB_GROUP" "$DB_DIR"
sudo chmod 750 "$DB_DIR"   # Full owner, read/execute group, no access others

# Create backup directory with secure permissions
sudo mkdir -p "$DB_DIR/backups"
sudo chown "$DB_USER:$DB_GROUP" "$DB_DIR/backups"
sudo chmod 700 "$DB_DIR/backups"  # Full access owner only

echo "Database security hardening completed"
```

### Access Control

```python
import pwd
import grp
import os
import stat

class DatabaseSecurity:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def verify_permissions(self):
        """Verify database file has secure permissions"""
        stat_info = os.stat(self.db_path)
        
        # Check file permissions (should be 640 or more restrictive)
        mode = stat.filemode(stat_info.st_mode)
        if stat_info.st_mode & 0o077:  # Others have any permissions
            raise SecurityError("Database file has insecure permissions")
        
        # Check ownership
        owner_name = pwd.getpwuid(stat_info.st_uid).pw_name
        group_name = grp.getgrgid(stat_info.st_gid).gr_name
        
        return {
            'permissions': mode,
            'owner': owner_name,
            'group': group_name,
            'secure': True
        }
    
    def audit_access(self):
        """Audit database access patterns"""
        # Check for unusual access patterns
        # Log security events
        # Monitor for unauthorized access attempts
        pass
```

## 🛠️ Troubleshooting Guide

### Common Production Issues

#### Database Lock Issues
```python
def resolve_database_locks():
    """Resolve common database locking issues"""
    
    # Check for long-running transactions
    with sqlite3.connect("logs.db") as conn:
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode = WAL")
        
        # Set busy timeout
        conn.execute("PRAGMA busy_timeout = 30000")  # 30 seconds
        
        # Check for blocking processes
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("ROLLBACK")
            print("No database locks detected")
        except sqlite3.OperationalError as e:
            print(f"Database lock detected: {e}")
            # Kill blocking processes or wait
```

#### Performance Degradation
```python
def diagnose_performance_issues():
    """Diagnose and resolve performance problems"""
    
    with sqlite3.connect("logs.db") as conn:
        # Check if statistics are outdated
        analyze_needed = conn.execute("""
            SELECT COUNT(*) FROM sqlite_stat1 WHERE tbl = 'logs'
        """).fetchone()[0] == 0
        
        if analyze_needed:
            print("Running ANALYZE to update statistics...")
            conn.execute("ANALYZE")
            
        # Check for fragmentation
        page_count = conn.execute("PRAGMA page_count").fetchone()[0]
        freelist_count = conn.execute("PRAGMA freelist_count").fetchone()[0]
        
        fragmentation_ratio = freelist_count / page_count if page_count > 0 else 0
        
        if fragmentation_ratio > 0.1:  # More than 10% fragmentation
            print("High fragmentation detected, running VACUUM...")
            conn.execute("VACUUM")
            
        # Check index usage
        conn.execute("PRAGMA optimize")
```

---

## 📚 Additional Resources

### Monitoring Dashboards
- **Grafana Dashboard** - Visualize Debuggle database metrics
- **Custom Monitoring** - Integration with existing monitoring solutions
- **Alert Rules** - PagerDuty, OpsGenie integration examples

### Deployment Guides  
- **Docker Production** - Production-ready containerization
- **Kubernetes** - Scalable deployment patterns
- **Load Balancing** - Multi-instance deployment strategies

### Integration Examples
- **CI/CD Pipelines** - Automated testing and deployment
- **Backup Strategies** - Enterprise backup and disaster recovery
- **Compliance** - GDPR, SOC2, HIPAA configuration examples

---

*This guide represents best practices developed through production deployments. Adapt recommendations based on your specific infrastructure and requirements.*