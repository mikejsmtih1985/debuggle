# 📊 Debuggle Database Schema - Complete Data Model Reference

## 📖 Overview

This document provides a comprehensive reference for Debuggle's SQLite database schema, designed for developers, database administrators, and anyone working with Debuggle's data persistence layer.

## 🗄️ Core Schema

### Primary Table: `logs`

The `logs` table is the heart of Debuggle's data model, storing all error log entries with comprehensive metadata and indexing.

```sql
CREATE TABLE logs (
    log_id TEXT PRIMARY KEY,              -- Unique identifier (SHA-256 based)
    timestamp DATETIME NOT NULL,          -- ISO 8601 formatted timestamp
    original_log TEXT NOT NULL,           -- Raw, unprocessed log content
    processed_log TEXT NOT NULL,          -- Cleaned and formatted log
    summary TEXT,                         -- AI-generated summary (nullable)
    tags TEXT,                           -- JSON array of string tags
    severity TEXT NOT NULL,              -- Severity level enum
    language TEXT NOT NULL,              -- Detected programming language
    metadata TEXT,                       -- JSON object with context data
    project_name TEXT,                   -- Associated project identifier
    file_path TEXT,                      -- Source file path (when available)
    source TEXT DEFAULT 'api',           -- Ingestion method
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- Record creation time
);
```

### Field Specifications

#### `log_id` (TEXT PRIMARY KEY)
- **Purpose:** Unique identifier for each log entry
- **Format:** SHA-256 hash of log content, timestamp, and context
- **Example:** `"a1b2c3d4e5f6789012345678901234567890abcdef"`
- **Uniqueness:** Guaranteed unique even for identical error messages
- **Indexing:** Primary key automatically indexed

#### `timestamp` (DATETIME NOT NULL)
- **Purpose:** When the original error occurred (not when it was stored)
- **Format:** ISO 8601 datetime string (`YYYY-MM-DD HH:MM:SS`)
- **Example:** `"2025-01-15 14:30:22"`
- **Timezone:** UTC (recommended) or local time with consistent usage
- **Constraints:** NOT NULL, automatically indexed

#### `original_log` (TEXT NOT NULL)
- **Purpose:** Raw, unmodified error message or stack trace
- **Content:** Exactly as received from application/system
- **Example:** 
  ```
  Traceback (most recent call last):
    File "app.py", line 42, in main
      result = users[999]
  IndexError: list index out of range
  ```
- **Size:** No limit (SQLite TEXT can store up to 1 billion characters)
- **Encoding:** UTF-8

#### `processed_log` (TEXT NOT NULL)
- **Purpose:** Cleaned, formatted, human-readable version
- **Content:** Enhanced with emojis, colors, and structure
- **Example:**
  ```
  🚨 [PYTHON] IndexError on line 42
  📍 File: app.py, Function: main
  💡 Problem: Tried to access index 999, but list doesn't have that many items
  ```
- **Processing:** Applied by Debuggle's analysis engine
- **Formatting:** Optimized for terminal and web display

#### `summary` (TEXT, NULLABLE)
- **Purpose:** AI-generated brief description of the error
- **Content:** 1-2 sentence explanation suitable for dashboards
- **Example:** `"Array index out of bounds error when accessing user data"`
- **Null handling:** NULL for errors that couldn't be summarized
- **Length:** Typically 50-200 characters

#### `tags` (TEXT, JSON ARRAY)
- **Purpose:** Classification labels for categorization and filtering
- **Format:** JSON array of strings
- **Example:** `["indexerror", "python", "array", "bounds-check"]`
- **Categories:** Error types, languages, patterns, severity indicators
- **Usage:** Enable fast filtering and trend analysis
- **Schema:**
  ```json
  [
    "error_type",      // indexerror, nullpointer, etc.
    "language",        // python, javascript, java, etc.
    "category",        // logic, syntax, runtime, etc.
    "pattern",         // array-bounds, null-deref, etc.
    "component"        // database, api, ui, etc.
  ]
  ```

#### `severity` (TEXT NOT NULL)
- **Purpose:** Error criticality level
- **Values:** Enum-constrained to specific levels
- **Options:**
  - `"trace"` - Detailed debugging information
  - `"debug"` - Development debugging messages
  - `"info"` - Informational messages
  - `"warning"` - Potential issues, not errors
  - `"error"` - Actual errors requiring attention
  - `"critical"` - Severe errors that may cause system failure
- **Example:** `"error"`
- **Indexing:** Indexed for fast severity-based queries

#### `language` (TEXT NOT NULL)
- **Purpose:** Programming language detection
- **Values:** Language identifiers (lowercase)
- **Common values:** `python`, `javascript`, `java`, `c#`, `c++`, `go`, `rust`
- **Special values:** `unknown`, `mixed`, `shell`
- **Example:** `"python"`
- **Detection:** Based on stack trace patterns, file extensions, syntax

#### `metadata` (TEXT, JSON OBJECT)
- **Purpose:** Extensible context information
- **Format:** JSON object with flexible schema
- **Example:**
  ```json
  {
    "file_line": 42,
    "function_name": "main",
    "exception_type": "IndexError",
    "stack_depth": 3,
    "environment": "development",
    "python_version": "3.9.1",
    "dependencies": ["flask==2.0.1", "requests==2.25.1"],
    "git_commit": "abc123def",
    "user_agent": "curl/7.68.0"
  }
  ```
- **Extensibility:** New fields can be added without schema changes
- **Querying:** Can be queried using SQLite JSON functions

#### `project_name` (TEXT, NULLABLE)
- **Purpose:** Associated project or application identifier
- **Content:** Project name from configuration or detection
- **Example:** `"my-web-app"`, `"mobile-api"`, `"data-pipeline"`
- **Usage:** Multi-project filtering and organization
- **Detection:** From git repository, config files, or explicit setting

#### `file_path` (TEXT, NULLABLE)
- **Purpose:** Source file where error occurred
- **Content:** Relative or absolute file path
- **Example:** `"src/main.py"`, `"/app/controllers/user.py"`
- **Normalization:** Paths normalized to forward slashes
- **Privacy:** May be null for security in production environments

#### `source` (TEXT, DEFAULT 'api')
- **Purpose:** How the log was ingested into Debuggle
- **Values:**
  - `"api"` - HTTP API endpoint
  - `"cli"` - Command line interface
  - `"upload"` - File upload via web interface
  - `"webhook"` - External system webhook
  - `"import"` - Bulk import operation
- **Example:** `"cli"`
- **Usage:** Track ingestion methods for analytics

#### `created_at` (DATETIME, DEFAULT CURRENT_TIMESTAMP)
- **Purpose:** When the record was inserted into database
- **Format:** ISO 8601 datetime
- **Difference from `timestamp`:** `timestamp` = when error occurred, `created_at` = when stored
- **Usage:** Audit trails, replication timing, cleanup operations

## 📈 Performance Indexes

### Primary Indexes
```sql
-- Automatic primary key index
-- Covers: Unique lookups by log_id

-- Time-based queries (most common pattern)
CREATE INDEX idx_timestamp ON logs(timestamp);
-- Covers: Date ranges, recent errors, time-series analysis

-- Severity filtering (critical for alerting)
CREATE INDEX idx_severity ON logs(severity);
-- Covers: Error dashboards, severity-based filtering

-- Language-specific analysis
CREATE INDEX idx_language ON logs(language);
-- Covers: Language-specific error patterns

-- Project organization
CREATE INDEX idx_project ON logs(project_name);
-- Covers: Multi-project deployments, tenant isolation

-- Source tracking
CREATE INDEX idx_source ON logs(source);
-- Covers: Ingestion method analytics
```

### Composite Indexes (Advanced)
```sql
-- Common query patterns
CREATE INDEX idx_severity_timestamp ON logs(severity, timestamp);
-- Covers: "Recent critical errors"

CREATE INDEX idx_project_language ON logs(project_name, language);
-- Covers: "Python errors in web-app project"

CREATE INDEX idx_language_timestamp ON logs(language, timestamp);
-- Covers: "Recent JavaScript errors"
```

## 🔍 Full-Text Search Schema

### Search Index Table
```sql
CREATE VIRTUAL TABLE search_fts USING fts5(
    log_id UNINDEXED,                    -- Link back to main logs table
    title,                               -- Searchable title/summary
    content,                             -- Searchable log content
    full_text,                           -- Combined searchable text
    language UNINDEXED,                  -- Filter by language
    severity UNINDEXED,                  -- Filter by severity
    timestamp UNINDEXED,                 -- Filter by time
    tags,                                -- Searchable tags
    error_type,                          -- Searchable error classification
    file_path,                           -- Searchable file paths
    user_id UNINDEXED,                   -- Pro/Enterprise: user filtering
    project_id UNINDEXED,                -- Pro/Enterprise: project filtering
    custom_fields                        -- Enterprise: extensible fields
);
```

### FTS5 Configuration
```sql
-- Advanced search configuration
CREATE VIRTUAL TABLE search_fts USING fts5(
    content,
    tags,
    error_type,
    file_path,
    tokenize='trigram',                  -- Support partial matches
    prefix='2,3'                         -- Enable prefix search
);
```

## 📊 Data Examples

### Sample Log Entry
```sql
INSERT INTO logs VALUES (
    'a1b2c3d4e5f67890123456789abcdef01234567',
    '2025-01-15 14:30:22',
    'Traceback (most recent call last):
  File "app.py", line 42, in main
    result = users[999]
IndexError: list index out of range',
    '🚨 [PYTHON] IndexError on line 42
📍 File: app.py, Function: main
💡 Problem: Tried to access index 999, but list doesn''t have that many items
🔧 Quick fix: Check list length before accessing',
    'Array index out of bounds when accessing user data',
    '["indexerror", "python", "array", "bounds-check", "logic-error"]',
    'error',
    'python',
    '{
        "file_line": 42,
        "function_name": "main",
        "exception_type": "IndexError",
        "stack_depth": 3,
        "environment": "development",
        "python_version": "3.9.1"
    }',
    'my-web-app',
    'app.py',
    'cli',
    '2025-01-15 14:30:25'
);
```

### Query Examples

#### Basic Queries
```sql
-- Recent errors (last 24 hours)
SELECT * FROM logs 
WHERE timestamp >= datetime('now', '-1 day') 
ORDER BY timestamp DESC;

-- Critical errors only
SELECT * FROM logs 
WHERE severity = 'critical' 
ORDER BY timestamp DESC;

-- Python errors in specific project
SELECT * FROM logs 
WHERE language = 'python' 
  AND project_name = 'my-web-app'
ORDER BY timestamp DESC;
```

#### Advanced Queries
```sql
-- Error frequency analysis
SELECT 
    severity,
    language,
    COUNT(*) as error_count,
    DATE(timestamp) as error_date
FROM logs 
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY severity, language, DATE(timestamp)
ORDER BY error_count DESC;

-- Top error patterns
SELECT 
    json_extract(metadata, '$.exception_type') as exception_type,
    COUNT(*) as frequency,
    language
FROM logs 
WHERE timestamp >= datetime('now', '-30 days')
  AND json_extract(metadata, '$.exception_type') IS NOT NULL
GROUP BY exception_type, language
ORDER BY frequency DESC
LIMIT 10;

-- Full-text search
SELECT logs.* 
FROM logs 
JOIN search_fts ON logs.log_id = search_fts.log_id
WHERE search_fts MATCH 'database connection timeout'
ORDER BY logs.timestamp DESC;
```

#### JSON Metadata Queries
```sql
-- Errors from specific Python version
SELECT * FROM logs 
WHERE json_extract(metadata, '$.python_version') LIKE '3.8%';

-- Errors from specific git commit
SELECT * FROM logs 
WHERE json_extract(metadata, '$.git_commit') = 'abc123def';

-- Errors with high stack depth (complex call chains)
SELECT * FROM logs 
WHERE CAST(json_extract(metadata, '$.stack_depth') AS INTEGER) > 10;
```

## 🔧 Schema Migrations

### Version Control
```sql
-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_version (version, description) 
VALUES (1, 'Initial schema with logs table and indexes');
```

### Migration Examples
```sql
-- Adding new column (backwards compatible)
ALTER TABLE logs ADD COLUMN user_id TEXT;
CREATE INDEX idx_user_id ON logs(user_id);

-- Adding new metadata field (no schema change needed)
-- Just start storing in the metadata JSON field

-- Adding new severity level
-- No schema change needed - it's a TEXT field
```

## 📏 Storage Estimation

### Size Calculations
- **Average log entry:** ~1-2 KB
- **Typical error with stack trace:** ~2-5 KB  
- **Complex metadata:** +500 bytes - 1 KB
- **Index overhead:** ~20-30% of data size

### Capacity Planning
```sql
-- Database size query
SELECT 
    page_count * page_size / 1024 / 1024 as size_mb,
    page_count,
    page_size
FROM pragma_page_count(), pragma_page_size();

-- Table-specific sizes
SELECT 
    name,
    pgsize,
    unused
FROM dbstat 
WHERE name = 'logs';
```

## 🛡️ Data Integrity

### Constraints
```sql
-- Severity constraint
CREATE TABLE logs (
    -- ... other fields ...
    severity TEXT NOT NULL CHECK (
        severity IN ('trace', 'debug', 'info', 'warning', 'error', 'critical')
    ),
    -- ... other fields ...
);

-- Timestamp constraint
CREATE TABLE logs (
    -- ... other fields ...
    timestamp DATETIME NOT NULL CHECK (
        timestamp >= '1970-01-01' AND timestamp <= '2100-01-01'
    ),
    -- ... other fields ...
);
```

### Validation Triggers
```sql
-- Validate JSON fields
CREATE TRIGGER validate_tags_json
BEFORE INSERT ON logs
WHEN NEW.tags IS NOT NULL AND json_valid(NEW.tags) = 0
BEGIN
    SELECT RAISE(ABORT, 'Invalid JSON in tags field');
END;

CREATE TRIGGER validate_metadata_json
BEFORE INSERT ON logs  
WHEN NEW.metadata IS NOT NULL AND json_valid(NEW.metadata) = 0
BEGIN
    SELECT RAISE(ABORT, 'Invalid JSON in metadata field');
END;
```

## 🔍 Query Optimization Tips

### Efficient Patterns
```sql
-- Use indexes effectively
SELECT * FROM logs 
WHERE timestamp >= ? AND timestamp < ?  -- Uses idx_timestamp
ORDER BY timestamp;

-- Combine indexed columns
SELECT * FROM logs 
WHERE severity = 'error' AND timestamp >= ?  -- Uses idx_severity_timestamp
ORDER BY timestamp DESC;

-- JSON queries with indexes
SELECT * FROM logs 
WHERE language = 'python'  -- Uses idx_language
  AND json_extract(metadata, '$.exception_type') = 'ValueError';
```

### Anti-patterns to Avoid
```sql
-- Avoid function calls on indexed columns
SELECT * FROM logs WHERE UPPER(language) = 'PYTHON';  -- Won't use index

-- Avoid leading wildcards in LIKE
SELECT * FROM logs WHERE log_id LIKE '%abc%';  -- Won't use index

-- Avoid OR conditions across different columns
SELECT * FROM logs WHERE severity = 'error' OR language = 'python';  -- Poor performance
```

---

*This schema is designed for high performance, data integrity, and extensibility while maintaining simplicity and SQLite compatibility.*