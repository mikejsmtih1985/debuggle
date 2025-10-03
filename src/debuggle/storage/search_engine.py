"""
🔍 DEBUGGLE SEARCH ENGINE - Lightning-Fast Error Discovery! ⚡

This module implements a powerful search engine that gracefully falls back to
SQLite FTS when Whoosh is not available, ensuring search always works!

🎯 MULTI-ENGINE APPROACH:
- 🏆 Primary: Whoosh (when available) - Advanced full-text search
- 🛡️ Fallback: SQLite FTS - Built-in Python, always works
- 🔄 Transparent: Same API regardless of backend
- 💰 Pro Features: Available with either backend

🏆 HIGH SCHOOL EXPLANATION:
Think of this like having two search engines for your error logs:
1. Premium search (Whoosh): Like Google for your errors - super smart
2. Backup search (SQLite): Like a phone book - always reliable
"""

import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, asdict

# Try to import Whoosh for advanced search
try:
    from whoosh import fields, index
    from whoosh.qparser import QueryParser, MultifieldParser
    from whoosh.query import Term, And, DateRange
    from whoosh.analysis import StemmingAnalyzer, StandardAnalyzer
    from whoosh.sorting import FieldFacet
    WHOOSH_AVAILABLE = True
except ImportError:
    WHOOSH_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Single search result with metadata."""
    log_id: str
    title: str
    content: str
    relevance_score: float
    timestamp: datetime
    severity: str = "info"
    language: str = "unknown"
    tags: Optional[List[str]] = None
    file_path: str = ""
    error_type: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class SearchAnalytics:
    """Analytics data for Pro tier users."""
    total_results: int
    search_time_ms: float
    suggested_queries: Optional[List[str]] = None
    error_trends: Optional[Dict[str, int]] = None
    related_errors: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.suggested_queries is None:
            self.suggested_queries = []
        if self.error_trends is None:
            self.error_trends = {}
        if self.related_errors is None:
            self.related_errors = []

class DebuggleSearchEngine:
    """
    🔍 Multi-backend search engine with graceful Whoosh/SQLite fallback.
    
    This class provides powerful search capabilities that work whether or not
    Whoosh is installed, ensuring search functionality is always available.
    """
    
    def __init__(self, index_dir: str = "search_index", tier: str = "free"):
        self.index_dir = Path(index_dir)
        self.tier = tier
        self.index_dir.mkdir(exist_ok=True)
        
        # Initialize the appropriate backend
        if WHOOSH_AVAILABLE:
            logger.info("🔍 Initializing Whoosh search engine (Pro features available)")
            self._init_whoosh()
        else:
            logger.info("🔍 Initializing SQLite FTS search engine (fallback mode)")
            self._init_sqlite_fts()
    
    def _init_whoosh(self):
        """Initialize Whoosh backend."""
        try:
            self.backend = "whoosh"
            self.schema = self._create_whoosh_schema()
            
            index_path = str(self.index_dir)
            if index.exists_in(index_path):
                self.index = index.open_dir(index_path)
            else:
                self.index = index.create_in(index_path, self.schema)
        except Exception as e:
            logger.warning(f"Failed to initialize Whoosh: {e}. Falling back to SQLite.")
            self._init_sqlite_fts()
    
    def _init_sqlite_fts(self):
        """Initialize SQLite FTS backend."""
        self.backend = "sqlite"
        self.db_path = self.index_dir / "search.db"
        self._create_sqlite_tables()
    
    def _create_whoosh_schema(self):
        """Create Whoosh schema."""
        schema_fields = {
            'log_id': fields.ID(stored=True, unique=True),
            'title': fields.TEXT(stored=True, analyzer=StemmingAnalyzer()),
            'content': fields.TEXT(stored=True, analyzer=StemmingAnalyzer()),
            'full_text': fields.TEXT(analyzer=StemmingAnalyzer()),
            'language': fields.KEYWORD(stored=True),
            'severity': fields.KEYWORD(stored=True),
            'timestamp': fields.DATETIME(stored=True),
            'date_str': fields.KEYWORD(stored=True),
            'tags': fields.KEYWORD(stored=True, commas=True),
            'error_type': fields.KEYWORD(stored=True),
            'file_path': fields.TEXT(stored=True),
        }
        
        # Pro tier fields
        if self.tier != "free":
            schema_fields.update({
                'user_id': fields.KEYWORD(stored=True),
                'project_id': fields.KEYWORD(stored=True)
            })
            
        if self.tier == "enterprise":
            schema_fields['custom_fields'] = fields.TEXT(stored=True)
        
        return fields.Schema(**schema_fields)
    
    def _create_sqlite_tables(self):
        """Create SQLite FTS tables."""
        with sqlite3.connect(self.db_path) as conn:
            # Create FTS table for search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS search_fts USING fts5(
                    log_id UNINDEXED,
                    title,
                    content,
                    full_text,
                    language UNINDEXED,
                    severity UNINDEXED,
                    timestamp UNINDEXED,
                    tags UNINDEXED,
                    error_type UNINDEXED,
                    file_path,
                    user_id UNINDEXED,
                    project_id UNINDEXED,
                    custom_fields
                )
            """)
            
            # Create metadata table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_metadata (
                    log_id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    severity TEXT,
                    language TEXT,
                    tags TEXT,
                    error_type TEXT,
                    file_path TEXT,
                    user_id TEXT,
                    project_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def add_log(self, log_data: Dict[str, Any]) -> bool:
        """Add a log entry to the search index."""
        try:
            if self.backend == "whoosh":
                return self._add_log_whoosh(log_data)
            else:
                return self._add_log_sqlite(log_data)
        except Exception as e:
            logger.error(f"Error adding log to search index: {e}")
            return False
    
    def _add_log_whoosh(self, log_data: Dict[str, Any]) -> bool:
        """Add log using Whoosh backend."""
        writer = self.index.writer()
        try:
            # Prepare document
            doc = {
                'log_id': log_data.get('id', ''),
                'title': log_data.get('title', ''),
                'content': log_data.get('content', ''),
                'full_text': f"{log_data.get('title', '')} {log_data.get('content', '')}",
                'language': log_data.get('language', 'unknown'),
                'severity': log_data.get('severity', 'info'),
                'timestamp': log_data.get('timestamp', datetime.now()),
                'date_str': log_data.get('timestamp', datetime.now()).strftime('%Y-%m-%d'),
                'tags': ','.join(log_data.get('tags', [])),
                'error_type': log_data.get('error_type', ''),
                'file_path': log_data.get('file_path', ''),
            }
            
            # Add Pro tier fields
            if self.tier != "free":
                doc.update({
                    'user_id': log_data.get('user_id', ''),
                    'project_id': log_data.get('project_id', '')
                })
            
            if self.tier == "enterprise":
                doc['custom_fields'] = json.dumps(log_data.get('custom_fields', {}))
            
            writer.add_document(**doc)
            writer.commit()
            return True
        except Exception as e:
            writer.cancel()
            raise e
    
    def _add_log_sqlite(self, log_data: Dict[str, Any]) -> bool:
        """Add log using SQLite FTS backend."""
        with sqlite3.connect(self.db_path) as conn:
            # Insert into FTS table
            conn.execute("""
                INSERT OR REPLACE INTO search_fts (
                    log_id, title, content, full_text, language, severity,
                    timestamp, tags, error_type, file_path, user_id, project_id, custom_fields
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_data.get('id', ''),
                log_data.get('title', ''),
                log_data.get('content', ''),
                f"{log_data.get('title', '')} {log_data.get('content', '')}",
                log_data.get('language', 'unknown'),
                log_data.get('severity', 'info'),
                log_data.get('timestamp', datetime.now()).isoformat(),
                ','.join(log_data.get('tags', [])),
                log_data.get('error_type', ''),
                log_data.get('file_path', ''),
                log_data.get('user_id', '') if self.tier != "free" else '',
                log_data.get('project_id', '') if self.tier != "free" else '',
                json.dumps(log_data.get('custom_fields', {})) if self.tier == "enterprise" else ''
            ))
            
            # Insert metadata
            conn.execute("""
                INSERT OR REPLACE INTO search_metadata (
                    log_id, timestamp, severity, language, tags, error_type, file_path, user_id, project_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_data.get('id', ''),
                log_data.get('timestamp', datetime.now()).isoformat(),
                log_data.get('severity', 'info'),
                log_data.get('language', 'unknown'),
                ','.join(log_data.get('tags', [])),
                log_data.get('error_type', ''),
                log_data.get('file_path', ''),
                log_data.get('user_id', '') if self.tier != "free" else '',
                log_data.get('project_id', '') if self.tier != "free" else ''
            ))
            
            conn.commit()
            return True
    
    def search(self, query: str, limit: int = 50, filters: Optional[Dict[str, Any]] = None) -> Tuple[List[SearchResult], Optional[SearchAnalytics]]:
        """
        Search the index with the given query and filters.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            filters: Optional filters (severity, date_range, etc.)
            
        Returns:
            Tuple of (search results, analytics for Pro tier)
        """
        start_time = datetime.now()
        
        try:
            if self.backend == "whoosh":
                results = self._search_whoosh(query, limit, filters or {})
            else:
                results = self._search_sqlite(query, limit, filters or {})
            
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Generate analytics for Pro tier
            analytics = None
            if self.tier != "free":
                analytics = SearchAnalytics(
                    total_results=len(results),
                    search_time_ms=search_time,
                    suggested_queries=self._generate_suggestions(query),
                    error_trends=self._get_error_trends(),
                    related_errors=self._get_related_errors(query)
                )
            
            return results, analytics
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return [], None
    
    def _search_whoosh(self, query: str, limit: int, filters: Dict[str, Any]) -> List[SearchResult]:
        """Search using Whoosh backend."""
        results = []
        
        with self.index.searcher() as searcher:
            # Create query parser
            parser = MultifieldParser(['title', 'content', 'full_text'], self.index.schema)
            parsed_query = parser.parse(query)
            
            # Apply filters
            if filters:
                # Add filter logic here
                pass
            
            # Execute search
            whoosh_results = searcher.search(parsed_query, limit=limit)
            
            for hit in whoosh_results:
                result = SearchResult(
                    log_id=hit['log_id'],
                    title=hit['title'],
                    content=hit['content'],
                    relevance_score=float(hit.score) if hit.score is not None else 0.0,
                    timestamp=hit['timestamp'],
                    severity=hit.get('severity', 'info'),
                    language=hit.get('language', 'unknown'),
                    tags=hit.get('tags', '').split(',') if hit.get('tags') else [],
                    file_path=hit.get('file_path', ''),
                    error_type=hit.get('error_type', '')
                )
                results.append(result)
        
        return results
    
    def _search_sqlite(self, query: str, limit: int, filters: Dict[str, Any]) -> List[SearchResult]:
        """Search using SQLite FTS backend."""
        results = []
        
        with sqlite3.connect(self.db_path) as conn:
            # Prepare FTS query
            fts_query = query.replace("'", "''")  # Escape quotes
            
            sql = """
                SELECT log_id, title, content, language, severity, timestamp, 
                       tags, error_type, file_path, rank
                FROM search_fts 
                WHERE search_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """
            
            cursor = conn.execute(sql, (fts_query, limit))
            
            for row in cursor.fetchall():
                try:
                    timestamp = datetime.fromisoformat(row[5]) if row[5] else datetime.now()
                except (ValueError, TypeError):
                    timestamp = datetime.now()
                
                result = SearchResult(
                    log_id=row[0],
                    title=row[1] or '',
                    content=row[2] or '',
                    relevance_score=1.0,  # SQLite FTS doesn't provide detailed scoring
                    timestamp=timestamp,
                    severity=row[4] or 'info',
                    language=row[3] or 'unknown',
                    tags=row[6].split(',') if row[6] else [],
                    file_path=row[8] or '',
                    error_type=row[7] or ''
                )
                results.append(result)
        
        return results
    
    def _generate_suggestions(self, query: str) -> List[str]:
        """Generate search suggestions for Pro tier."""
        # Simple suggestion logic - can be enhanced
        suggestions = []
        
        if "error" in query.lower():
            suggestions.extend(["exception", "failure", "crash"])
        if "connection" in query.lower():
            suggestions.extend(["network", "timeout", "refused"])
        if "database" in query.lower():
            suggestions.extend(["sql", "query", "connection"])
        
        return suggestions[:5]
    
    def _get_error_trends(self) -> Dict[str, int]:
        """Get error trends for Pro tier analytics."""
        trends = {}
        
        if self.backend == "sqlite":
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("""
                        SELECT error_type, COUNT(*) as count
                        FROM search_metadata 
                        WHERE timestamp > datetime('now', '-7 days')
                        GROUP BY error_type
                        ORDER BY count DESC
                        LIMIT 10
                    """)
                    
                    for row in cursor.fetchall():
                        if row[0]:
                            trends[row[0]] = row[1]
            except Exception as e:
                logger.error(f"Error getting trends: {e}")
        
        return trends
    
    def _get_related_errors(self, query: str) -> List[str]:
        """Get related errors for Pro tier analytics."""
        # Simple related error logic
        related = []
        
        if "index" in query.lower():
            related.extend(["IndexError", "KeyError", "list index out of range"])
        if "attribute" in query.lower():
            related.extend(["AttributeError", "NoneType", "missing attribute"])
        if "import" in query.lower():
            related.extend(["ImportError", "ModuleNotFoundError", "No module named"])
        
        return related[:5]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics."""
        stats = {
            'backend': self.backend,
            'tier': self.tier,
            'whoosh_available': WHOOSH_AVAILABLE,
            'total_documents': 0
        }
        
        try:
            if self.backend == "whoosh":
                with self.index.searcher() as searcher:
                    stats['total_documents'] = searcher.doc_count()
            else:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM search_fts")
                    stats['total_documents'] = cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
        
        return stats

# Export the main class
__all__ = ['DebuggleSearchEngine', 'SearchResult', 'SearchAnalytics']