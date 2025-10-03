"""
🏛️ DEBUGGLE DATA WAREHOUSE - Where All Our Error History Lives! 🏛️

Think of this module as a combination library and museum that stores and
organizes all the error logs that come through Debuggle. Just like how
a library keeps books organized so you can find them later, and a museum
preserves important artifacts, this storage system keeps all log data
safe and searchable.

🏆 HIGH SCHOOL EXPLANATION:
Imagine you're building a digital filing cabinet for a school's office:
- They need to keep student records for several years (log retention)
- Records need to be organized so they can be found quickly (indexing)
- Old records need to be deleted automatically (retention policies)
- The system needs to handle lots of records efficiently (performance)

This storage system does the same thing but for error logs instead of student records!

WHY LOCAL STORAGE INSTEAD OF CLOUD:
Following our "local alternatives" approach, we use SQLite instead of
cloud databases like AWS RDS or Google Cloud SQL. This means:
✅ No external dependencies or API keys needed
✅ Complete data privacy - logs never leave your server
✅ No monthly cloud bills or usage limits
✅ Works offline and in air-gapped environments
✅ Easy backups and migrations (just copy the database file)

WHAT THIS MODULE PROVIDES:
📊 Database Models - Like forms that define what data we store
🔍 Search Engine - Like a library's card catalog system
📅 Retention Management - Like automatically removing old files
📈 Statistics - Like reporting on what types of errors we see most
🛡️ Data Privacy - Like keeping everything secure and local
"""

from .database import DatabaseManager, LogEntry, LogStats
from .retention import RetentionManager
from .search import SearchManager

__version__ = "1.0.0"
__all__ = [
    "DatabaseManager", 
    "LogEntry", 
    "LogStats",
    "RetentionManager",
    "SearchManager"
]