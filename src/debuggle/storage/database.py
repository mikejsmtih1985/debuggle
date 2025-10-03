"""
🗄️ DEBUGGLE DATABASE MANAGER - The Digital Filing Cabinet! 🗄️

Think of this module as the master librarian who manages a sophisticated
digital library system. Just like how a librarian knows exactly where
every book is stored and can quickly find what you're looking for,
this DatabaseManager knows where every error log is stored and can
retrieve them lightning-fast!

🏆 HIGH SCHOOL EXPLANATION:
Imagine you're organizing a massive collection of documents:
- Each document needs a unique ID number (like a library book barcode)
- Documents are sorted by date, type, and importance (database indexes)
- You need quick ways to find specific documents (database queries)
- Old documents get moved to storage or destroyed (retention policies)
- You track statistics about your collection (analytics)

That's exactly what this database system does for error logs!

DATABASE CHOICE - WHY SQLITE?
We use SQLite instead of big databases like PostgreSQL because:
🚀 No Setup Required - Works immediately, no installation needed
📱 Self-Contained - Entire database is just one file you can copy/backup
🔒 No Network Security Risks - Database runs in your application process
⚡ Extremely Fast - Perfect for read-heavy workloads like log analysis
💰 Zero Cost - No licensing fees or cloud bills
🧳 Portable - Move your entire database by copying one file

This is like using a high-quality, portable filing cabinet instead of
renting space in a warehouse across town!
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class TierLevel(str, Enum):
    """🎯 DEBUGGLE TIER LEVELS - Feature Access Control"""
    FREE = "free"           # Basic error analysis, 7-day retention
    PRO = "pro"             # Advanced retention, search, analytics  
    ENTERPRISE = "enterprise" # Custom integrations, SSO, compliance


class LogSeverity(str, Enum):
    """
    🌡️ ERROR TEMPERATURE SCALE - How Serious Is This Problem?
    
    Just like how doctors use different urgency levels in a hospital
    (stable, urgent, critical), we categorize errors by how serious
    they are so we can prioritize which ones need immediate attention.
    """
    TRACE = "trace"      # 🔍 Detective work - very detailed info for debugging
    DEBUG = "debug"      # 🐛 Developer notes - helpful during development  
    INFO = "info"        # ℹ️  Normal operations - "everything is working fine"
    WARNING = "warning"  # ⚠️  Caution - something unusual but not broken
    ERROR = "error"      # ❌ Problem - something is definitely wrong
    CRITICAL = "critical" # 🚨 Emergency - system might crash or lose data


@dataclass
class LogEntry:
    """
    📋 INDIVIDUAL LOG RECORD - One Complete Error Report
    
    Think of this as a medical chart for one patient visit to the hospital.
    Each LogEntry contains everything we know about one specific error
    that occurred, organized in a standard format so we can easily
    compare and analyze different errors.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like filling out a standard form every time something noteworthy happens:
    - Student ID (log_id) - unique identifier
    - Date & Time (timestamp) - when it happened  
    - What Happened (original_log) - the raw details
    - Diagnosis (summary) - what we think the problem is
    - Category (tags) - what type of problem it is
    - Severity (severity) - how serious it is
    - Treatment Notes (processed_log) - cleaned up, easy-to-read version
    """
    
    # 🏷️ UNIQUE IDENTIFIER - Like a patient ID number or case number
    # This ensures we never lose track of any log entry, even if we have
    # thousands with similar content
    log_id: str
    
    # 🕒 WHEN IT HAPPENED - Precise timestamp of when the error occurred
    # Like the "time of injury" on an accident report
    timestamp: datetime
    
    # 📝 RAW ERROR DATA - The original, unprocessed error message
    # Like the initial 911 call transcript before any interpretation
    original_log: str
    
    # ✨ CLEANED VERSION - Our nicely formatted, easy-to-read version
    # Like a doctor's clean summary after examining all the messy symptoms
    processed_log: str
    
    # 🧠 AI SUMMARY - Our intelligent explanation of what went wrong
    # Like a doctor explaining "what this means in plain English"
    summary: Optional[str]
    
    # 🏷️ CATEGORY TAGS - Labels that help us organize and search errors
    # Like putting colored stickers on files: "urgent", "billing", "medical"
    tags: List[str]
    
    # 🌡️ SEVERITY LEVEL - How serious this error is (using our enum above)
    # Like triage levels in an emergency room: green, yellow, red
    severity: LogSeverity
    
    # 💻 PROGRAMMING LANGUAGE - What language the error came from
    # Like noting whether a patient came from the "Python ward" or "Java ward"
    language: str
    
    # 📊 METADATA - Extra technical details about processing this log
    # Like additional notes that might be helpful for specialists
    metadata: Dict[str, Any]
    
    # 🗂️ PROJECT CONTEXT - Which project/system this error came from
    # Like noting which department or building the incident occurred in
    project_name: Optional[str] = None
    
    # 📁 FILE LOCATION - Specific file where the error occurred
    # Like noting the exact room number where an incident happened
    file_path: Optional[str] = None
    
    # 🏥 PROCESSING SOURCE - How this log entered our system
    # Like noting "walked in", "ambulance", "helicopter" for hospital patients
    source: str = "api"  # api, file_upload, websocket, etc.


@dataclass 
class LogStats:
    """
    📈 LOG ANALYTICS DASHBOARD - The Big Picture View
    
    Think of this as the hospital administrator's monthly report that
    shows patterns and trends across all patients. Instead of looking
    at individual cases, this gives us the bird's-eye view of what's
    happening across our entire error monitoring system.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like creating a summary report for the school principal:
    - How many incidents happened this month?
    - What were the most common types of problems?
    - Which grades/departments had the most issues?
    - Are problems getting better or worse over time?
    - What should we focus on improving?
    """
    
    # 📊 BASIC COUNTS - The fundamental "how many" statistics
    total_logs: int           # Total number of log entries we've seen
    logs_today: int          # How many happened just today
    logs_this_week: int      # How many happened this week
    logs_this_month: int     # How many happened this month
    
    # 🏆 TOP CATEGORIES - What problems happen most often
    # Like a "top 10 list" of the most common types of errors
    top_error_types: Dict[str, int]      # Most common error tags
    top_languages: Dict[str, int]        # Most common programming languages
    top_severity_levels: Dict[str, int]  # Most common severity levels
    
    # 📈 TRENDS - Are things getting better or worse?
    # Like tracking whether school disciplinary incidents are increasing
    errors_per_day_last_week: List[int]  # Daily error counts for the last 7 days
    severity_trends: Dict[str, List[int]] # How each severity level is trending
    
    # 🕒 TIMING PATTERNS - When do errors happen most?
    # Like knowing that most hospital visits happen on weekends
    busiest_hours: Dict[int, int]        # Which hours of the day see most errors
    busiest_days: Dict[str, int]         # Which days of the week see most errors
    
    # 📅 DATA FRESHNESS - How current is our information?
    oldest_log_date: Optional[datetime]  # When we started collecting data
    newest_log_date: Optional[datetime]  # Most recent log we processed
    last_updated: datetime               # When we calculated these statistics


class DatabaseManager:
    """
    🏛️ THE MASTER LIBRARIAN - Managing Our Digital Error Library!
    
    Think of this class as the head librarian of a massive digital library
    that specializes in error reports. This librarian knows exactly:
    - Where every error report is stored (database location)
    - How to organize new reports when they arrive (insert operations)
    - How to find specific reports quickly (search queries)
    - When to remove old reports to save space (retention policies)
    - How to create summary reports about the collection (analytics)
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like the person who manages the school's record-keeping system:
    - Sets up the filing system (database schema)
    - Files new documents in the right place (store logs)
    - Helps people find what they're looking for (search functions)
    - Maintains the system and keeps it organized (cleanup tasks)
    - Generates reports for administrators (analytics)
    
    The DatabaseManager handles all interaction with our SQLite database,
    making sure data is stored safely and can be retrieved quickly!
    """
    
    def __init__(self, database_path: str = "logs.db"):
        """
        🏗️ SETTING UP OUR DIGITAL LIBRARY
        
        When we create a new DatabaseManager, it's like a librarian
        setting up a new library branch:
        1. Choose the location (database file path)
        2. Set up the catalog system (database schema)  
        3. Install the filing cabinets (create tables)
        4. Prepare the indexing system (database indexes)
        
        This makes sure everything is ready to start storing and
        organizing error logs efficiently!
        """
        # 📍 LIBRARY LOCATION - where our database file will live
        # Like choosing the building address for our new library branch
        self.database_path = Path(database_path)
        
        # 📚 SETUP THE LIBRARY - create database tables and structure
        # Like installing all the shelves, catalog systems, and organization tools
        self._initialize_database()
        
        # ✅ READY FOR BUSINESS - log that our library is open!
        logger.info(f"Database manager initialized with database at: {self.database_path}")
    
    def _initialize_database(self):
        """
        🏗️ BUILDING THE LIBRARY INFRASTRUCTURE
        
        This is like the construction phase of building a new library:
        - Install the card catalog system (logs table)
        - Set up the indexing system (database indexes for fast searches)
        - Create the statistics office (prepared for analytics)
        - Install the security system (data integrity constraints)
        
        We only need to do this once when the library first opens!
        """
        with sqlite3.connect(self.database_path) as conn:
            # 📋 CREATE THE MAIN CATALOG TABLE - where all log entries live
            # This is like designing the main filing system for our library
            conn.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    log_id TEXT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    original_log TEXT NOT NULL,
                    processed_log TEXT NOT NULL,
                    summary TEXT,
                    tags TEXT, -- JSON array of strings
                    severity TEXT NOT NULL,
                    language TEXT NOT NULL,
                    metadata TEXT, -- JSON object
                    project_name TEXT,
                    file_path TEXT,
                    source TEXT DEFAULT 'api',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 🗂️ CREATE PERFORMANCE INDEXES - make searching lightning fast
            # This is like creating a sophisticated cross-reference system
            # so librarians can find any book in seconds instead of hours
            
            # 📅 TIME-BASED INDEX - quickly find logs from specific dates
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)')
            
            # 🏷️ TAG-BASED INDEX - quickly find logs with specific tags
            conn.execute('CREATE INDEX IF NOT EXISTS idx_severity ON logs(severity)')
            
            # 💻 LANGUAGE INDEX - quickly find logs from specific programming languages
            conn.execute('CREATE INDEX IF NOT EXISTS idx_language ON logs(language)')
            
            # 📁 PROJECT INDEX - quickly find logs from specific projects
            conn.execute('CREATE INDEX IF NOT EXISTS idx_project ON logs(project_name)')
            
            # 🕒 CREATION TIME INDEX - for retention and cleanup operations
            conn.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON logs(created_at)')
            
            # 💾 SAVE ALL CHANGES - make sure our library setup is permanent
            conn.commit()
            
        logger.info("Database schema initialized successfully")
    
    def store_log(self, log_entry: LogEntry) -> bool:
        """
        📚 FILING A NEW ERROR REPORT - Adding to Our Library Collection!
        
        This is like when someone brings a new document to the library
        and the librarian carefully files it in exactly the right place
        so it can be found later. We take the LogEntry (like a completed
        form) and store it permanently in our database.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like when a student brings a form to the office:
        1. Check that all required fields are filled out
        2. Assign it a unique filing number
        3. Put it in the right filing cabinet drawer
        4. Update the index so it can be found later
        5. Confirm it was filed successfully
        
        Returns True if successfully stored, False if something went wrong.
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                # 📝 PREPARE THE FILING DATA - convert our LogEntry to database format
                # Like transcribing information from a handwritten form to a computer system
                conn.execute('''
                    INSERT OR REPLACE INTO logs (
                        log_id, timestamp, original_log, processed_log, summary,
                        tags, severity, language, metadata, project_name, 
                        file_path, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    log_entry.log_id,
                    log_entry.timestamp,
                    log_entry.original_log,
                    log_entry.processed_log,
                    log_entry.summary,
                    json.dumps(log_entry.tags),  # Convert list to JSON string
                    log_entry.severity.value,
                    log_entry.language,
                    json.dumps(log_entry.metadata),  # Convert dict to JSON string
                    log_entry.project_name,
                    log_entry.file_path,
                    log_entry.source
                ))
                
                # 💾 COMMIT THE TRANSACTION - make the storage permanent
                conn.commit()
                
            # ✅ SUCCESS! - log that we successfully filed this document
            logger.debug(f"Successfully stored log entry: {log_entry.log_id}")
            return True
            
        except Exception as e:
            # ❌ FILING ERROR - something went wrong during storage
            logger.error(f"Failed to store log entry {log_entry.log_id}: {e}")
            return False
    
    def get_log(self, log_id: str) -> Optional[LogEntry]:
        """
        🔍 FINDING A SPECIFIC ERROR REPORT - Library Lookup Service!
        
        This is like when someone comes to the library with a specific
        call number and asks "can you find this exact book for me?"
        We use the unique log_id to locate and retrieve one specific
        error report from our entire collection.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like looking up a student's file by their student ID number:
        1. Go to the filing system
        2. Find the drawer for that ID number
        3. Pull out the complete file
        4. Return a copy of all the information
        
        Returns the complete LogEntry if found, or None if it doesn't exist.
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                # 🎯 PRECISE SEARCH - look for exactly this log_id
                cursor = conn.execute('''
                    SELECT log_id, timestamp, original_log, processed_log, summary,
                           tags, severity, language, metadata, project_name, 
                           file_path, source
                    FROM logs 
                    WHERE log_id = ?
                ''', (log_id,))
                
                # 📋 GET THE RESULTS - did we find anything?
                row = cursor.fetchone()
                
                if row:
                    # 🔄 CONVERT BACK TO LOGENTRY - reconstruct the original object
                    # Like taking the filed paperwork and putting it back in the original format
                    return LogEntry(
                        log_id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        original_log=row[2],
                        processed_log=row[3],
                        summary=row[4],
                        tags=json.loads(row[5]) if row[5] else [],
                        severity=LogSeverity(row[6]),
                        language=row[7],
                        metadata=json.loads(row[8]) if row[8] else {},
                        project_name=row[9],
                        file_path=row[10],
                        source=row[11]
                    )
                else:
                    # 📭 NOT FOUND - no log with this ID exists
                    return None
                    
        except Exception as e:
            # ❌ SEARCH ERROR - something went wrong during lookup
            logger.error(f"Failed to retrieve log {log_id}: {e}")
            return None
    
    def search_logs(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[LogSeverity] = None,
        language: Optional[str] = None,
        tags: Optional[List[str]] = None,
        project_name: Optional[str] = None,
        text_search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[LogEntry]:
        """
        🔍 ADVANCED LIBRARY SEARCH - Finding Multiple Related Documents!
        
        This is like using the library's advanced search system where you can
        say "find me all books about Python programming, published between
        2020-2023, with 'error' in the title, sorted by date, give me the
        first 50 results." This search function lets you filter logs using
        multiple criteria to find exactly what you're looking for.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like searching the school's database for specific student records:
        - Find all students from specific grades (severity filter)
        - Who were enrolled between certain dates (date range)
        - Taking specific classes (language/project filters)
        - With certain achievements (tags filter)  
        - Whose names contain certain text (text search)
        - Return only the first 20 results (limit/offset)
        
        This is much more powerful than looking up one specific record!
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                # 🏗️ BUILD THE SEARCH QUERY - construct our library search
                # Like building a complex question for the library catalog system
                
                query = "SELECT log_id, timestamp, original_log, processed_log, summary, tags, severity, language, metadata, project_name, file_path, source FROM logs WHERE 1=1"
                params = []
                
                # 📅 DATE RANGE FILTER - "show me only logs from this time period"
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date)
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date)
                
                # 🌡️ SEVERITY FILTER - "show me only critical errors"
                if severity:
                    query += " AND severity = ?"
                    params.append(severity.value)
                
                # 💻 LANGUAGE FILTER - "show me only Python errors"
                if language:
                    query += " AND language = ?"
                    params.append(language)
                
                # 📁 PROJECT FILTER - "show me only errors from this project"
                if project_name:
                    query += " AND project_name = ?"
                    params.append(project_name)
                
                # 🔍 TEXT SEARCH - "show me logs containing this text"
                if text_search:
                    query += " AND (original_log LIKE ? OR processed_log LIKE ? OR summary LIKE ?)"
                    search_term = f"%{text_search}%"
                    params.extend([search_term, search_term, search_term])
                
                # 🏷️ TAG SEARCH - "show me logs with any of these tags"
                if tags:
                    tag_conditions = []
                    for tag in tags:
                        tag_conditions.append("tags LIKE ?")
                        params.append(f"%{tag}%")
                    query += f" AND ({' OR '.join(tag_conditions)})"
                
                # 📊 SORT AND LIMIT - organize results and don't return too many
                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                # 🎯 EXECUTE THE SEARCH - run our complex query
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                # 🔄 CONVERT RESULTS - turn database rows back into LogEntry objects
                results = []
                for row in rows:
                    log_entry = LogEntry(
                        log_id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        original_log=row[2],
                        processed_log=row[3],
                        summary=row[4],
                        tags=json.loads(row[5]) if row[5] else [],
                        severity=LogSeverity(row[6]),
                        language=row[7],
                        metadata=json.loads(row[8]) if row[8] else {},
                        project_name=row[9],
                        file_path=row[10],
                        source=row[11]
                    )
                    results.append(log_entry)
                
                return results
                
        except Exception as e:
            # ❌ SEARCH ERROR - something went wrong during the complex search
            logger.error(f"Failed to search logs: {e}")
            return []
    
    def delete_logs_older_than(self, days: int) -> int:
        """
        🗑️ ARCHIVE CLEANUP - Removing Old Documents to Save Space!
        
        This is like the library's policy of removing old newspapers
        and magazines after a certain time to make room for new ones.
        We automatically delete log entries older than the specified
        number of days to prevent our database from growing too large.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like cleaning out old student files at the end of each school year:
        1. Calculate the cutoff date (today minus X days)
        2. Find all records older than that date
        3. Count how many we're going to remove
        4. Delete them permanently
        5. Report how many were removed
        
        Returns the number of log entries that were deleted.
        """
        try:
            # 📅 CALCULATE CUTOFF DATE - how far back should we keep logs?
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.database_path) as conn:
                # 📊 COUNT BEFORE DELETION - how many logs will be removed?
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM logs WHERE timestamp < ?", 
                    (cutoff_date,)
                )
                count_to_delete = cursor.fetchone()[0]
                
                # 🗑️ PERFORM THE DELETION - remove old logs permanently
                conn.execute(
                    "DELETE FROM logs WHERE timestamp < ?", 
                    (cutoff_date,)
                )
                
                # 💾 COMMIT THE CHANGES - make the deletion permanent
                conn.commit()
                
                # 📝 LOG THE CLEANUP - record what we did
                logger.info(f"Deleted {count_to_delete} log entries older than {days} days")
                return count_to_delete
                
        except Exception as e:
            # ❌ CLEANUP ERROR - something went wrong during deletion
            logger.error(f"Failed to delete old logs: {e}")
            return 0
    
    def get_statistics(self) -> LogStats:
        """
        📊 GENERATE LIBRARY ANALYTICS REPORT - The Big Picture View!
        
        This is like the library director creating a comprehensive annual
        report showing all the interesting patterns and trends in how the
        library is being used. Instead of looking at individual books,
        we're analyzing the entire collection to understand what's happening.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like creating a summary report for the school principal about
        student discipline records:
        - How many incidents total?
        - What types are most common?
        - Are incidents increasing or decreasing?
        - Which days/times see the most problems?
        - What trends should administrators be aware of?
        
        This helps identify patterns that wouldn't be obvious from
        looking at individual error reports!
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                # 📊 BASIC COUNTING STATISTICS
                # Like counting all the books in different sections of the library
                
                # Total count of all logs
                total_logs = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
                
                # Logs from specific time periods
                today = datetime.now().date()
                logs_today = conn.execute(
                    "SELECT COUNT(*) FROM logs WHERE DATE(timestamp) = ?", 
                    (today,)
                ).fetchone()[0]
                
                week_ago = datetime.now() - timedelta(days=7)
                logs_this_week = conn.execute(
                    "SELECT COUNT(*) FROM logs WHERE timestamp >= ?", 
                    (week_ago,)
                ).fetchone()[0]
                
                month_ago = datetime.now() - timedelta(days=30)
                logs_this_month = conn.execute(
                    "SELECT COUNT(*) FROM logs WHERE timestamp >= ?", 
                    (month_ago,)
                ).fetchone()[0]
                
                # 🏆 TOP CATEGORIES - What are the most common types?
                # Like finding out which sections of the library are most popular
                
                # Most common error severities
                severity_cursor = conn.execute('''
                    SELECT severity, COUNT(*) as count 
                    FROM logs 
                    GROUP BY severity 
                    ORDER BY count DESC 
                    LIMIT 10
                ''')
                top_severity_levels = dict(severity_cursor.fetchall())
                
                # Most common programming languages
                language_cursor = conn.execute('''
                    SELECT language, COUNT(*) as count 
                    FROM logs 
                    GROUP BY language 
                    ORDER BY count DESC 
                    LIMIT 10
                ''')
                top_languages = dict(language_cursor.fetchall())
                
                # Most common error types (from tags)
                # This is more complex because tags are stored as JSON arrays
                tag_counts = {}
                tag_cursor = conn.execute("SELECT tags FROM logs WHERE tags IS NOT NULL")
                for (tags_json,) in tag_cursor.fetchall():
                    if tags_json:
                        tags = json.loads(tags_json)
                        for tag in tags:
                            tag_counts[tag] = tag_counts.get(tag, 0) + 1
                
                # Get top 10 most common error types
                top_error_types = dict(
                    sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                )
                
                # 📈 TREND ANALYSIS - Are things getting better or worse?
                # Like tracking whether library usage is increasing over time
                
                errors_per_day = []
                for i in range(7):  # Last 7 days
                    day = datetime.now().date() - timedelta(days=i)
                    count = conn.execute(
                        "SELECT COUNT(*) FROM logs WHERE DATE(timestamp) = ?", 
                        (day,)
                    ).fetchone()[0]
                    errors_per_day.append(count)
                
                errors_per_day.reverse()  # Put in chronological order
                
                # Severity trends (simplified version)
                severity_trends = {}
                for severity in LogSeverity:
                    daily_counts = []
                    for i in range(7):
                        day = datetime.now().date() - timedelta(days=i)
                        count = conn.execute(
                            "SELECT COUNT(*) FROM logs WHERE DATE(timestamp) = ? AND severity = ?", 
                            (day, severity.value)
                        ).fetchone()[0]
                        daily_counts.append(count)
                    daily_counts.reverse()
                    severity_trends[severity.value] = daily_counts
                
                # 🕒 TIMING PATTERNS - When do errors happen most?
                # Like figuring out the busiest hours at the library
                
                # Busiest hours (0-23)
                hour_cursor = conn.execute('''
                    SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                    FROM logs 
                    GROUP BY hour 
                    ORDER BY count DESC
                ''')
                busiest_hours = {int(hour): count for hour, count in hour_cursor.fetchall()}
                
                # Busiest days of week
                day_cursor = conn.execute('''
                    SELECT strftime('%w', timestamp) as day_of_week, COUNT(*) as count
                    FROM logs 
                    GROUP BY day_of_week 
                    ORDER BY count DESC
                ''')
                # Convert day numbers to day names
                day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                busiest_days = {day_names[int(day)]: count for day, count in day_cursor.fetchall()}
                
                # 📅 DATA FRESHNESS - How current is our information?
                oldest_cursor = conn.execute("SELECT MIN(timestamp) FROM logs")
                oldest_result = oldest_cursor.fetchone()[0]
                oldest_log_date = datetime.fromisoformat(oldest_result) if oldest_result else None
                
                newest_cursor = conn.execute("SELECT MAX(timestamp) FROM logs")
                newest_result = newest_cursor.fetchone()[0]
                newest_log_date = datetime.fromisoformat(newest_result) if newest_result else None
                
                # 📋 COMPILE THE FINAL REPORT
                return LogStats(
                    total_logs=total_logs,
                    logs_today=logs_today,
                    logs_this_week=logs_this_week,
                    logs_this_month=logs_this_month,
                    top_error_types=top_error_types,
                    top_languages=top_languages,
                    top_severity_levels=top_severity_levels,
                    errors_per_day_last_week=errors_per_day,
                    severity_trends=severity_trends,
                    busiest_hours=busiest_hours,
                    busiest_days=busiest_days,
                    oldest_log_date=oldest_log_date,
                    newest_log_date=newest_log_date,
                    last_updated=datetime.now()
                )
                
        except Exception as e:
            # ❌ ANALYTICS ERROR - something went wrong generating statistics
            logger.error(f"Failed to generate statistics: {e}")
            # Return empty statistics as fallback
            return LogStats(
                total_logs=0,
                logs_today=0,
                logs_this_week=0,
                logs_this_month=0,
                top_error_types={},
                top_languages={},
                top_severity_levels={},
                errors_per_day_last_week=[0] * 7,
                severity_trends={},
                busiest_hours={},
                busiest_days={},
                oldest_log_date=None,
                newest_log_date=None,
                last_updated=datetime.now()
            )
    
    def create_log_id(self, log_content: str, timestamp: datetime) -> str:
        """
        🏷️ GENERATING UNIQUE LIBRARY CARD NUMBERS - Creating Unique IDs!
        
        This is like the library's system for creating unique barcode numbers
        for every book. Even if we get the exact same error message twice,
        each occurrence gets its own unique ID so we can track them separately.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like creating student ID numbers - even if two students have the same
        name, they get different ID numbers. We use a combination of:
        - The content of the error (like the student's name)
        - When it happened (like enrollment date)
        - A hash function (like a mathematical formula)
        
        This creates a unique fingerprint that's virtually impossible to duplicate.
        """
        # 🧮 CREATE UNIQUE FINGERPRINT - combine content and time
        # Like creating a unique serial number based on multiple factors
        content_hash = hashlib.sha256(
            f"{log_content}_{timestamp.isoformat()}".encode()
        ).hexdigest()
        
        # 📏 SHORTEN TO REASONABLE LENGTH - keep it manageable
        # Like using just the first part of a long serial number
        return f"log_{content_hash[:16]}"
    
    def vacuum_database(self):
        """
        🧹 LIBRARY MAINTENANCE - Optimizing Our Filing System!
        
        This is like the library's monthly maintenance where they:
        - Reorganize the shelves for better efficiency  
        - Compact the filing systems to save space
        - Update the catalog indexes for faster searches
        - General housekeeping to keep everything running smoothly
        
        SQLite's VACUUM command does the same thing for our database!
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                # 🧹 OPTIMIZE THE DATABASE - reorganize for better performance
                conn.execute("VACUUM")
                conn.commit()
            
            logger.info("Database vacuum completed successfully")
            
        except Exception as e:
            # ❌ MAINTENANCE ERROR - something went wrong during optimization
            logger.error(f"Failed to vacuum database: {e}")