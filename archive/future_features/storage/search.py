"""
🔍 DEBUGGLE SEARCH ENGINE - The Library's Master Catalog System! 🔍

Think of this module as a sophisticated library search system that can find
any book, article, or document using multiple search methods. Just like how
a modern library lets you search by title, author, subject, keywords, or
even full text content, this search engine provides multiple ways to find
specific error logs in our vast collection.

🏆 HIGH SCHOOL EXPLANATION:
Imagine you're building a search system for a massive school library:
- Simple search: "Find books with 'Python' in the title"
- Advanced search: "Find books about programming, published after 2020, by specific authors"
- Full-text search: "Find books that mention 'machine learning' anywhere in the content"
- Smart search: "Find similar books to this one I liked"
- Filters: "Show only books available for checkout, in the computer science section"

Our search engine does the same thing but for error logs instead of books!

WHY ADVANCED SEARCH MATTERS:
🎯 Precision - Find exactly what you're looking for, not thousands of results
🚀 Speed - Indexed searches return results in milliseconds  
🔗 Relationships - Find patterns and connections between related errors
📊 Analytics - Understand trends and patterns in your error data
🎨 Flexibility - Multiple search methods for different use cases
💡 Intelligence - Learn from searches to provide better suggestions

SEARCH CAPABILITIES PROVIDED:
🔤 Full-Text Search - Search inside log content using advanced text indexing
🏷️ Tag-Based Search - Find logs with specific error categories
📅 Time-Range Search - Find logs from specific time periods
🌡️ Severity Search - Filter by error severity levels
💻 Language Search - Find errors from specific programming languages
🎯 Complex Queries - Combine multiple search criteria
📈 Trending Search - Find patterns and frequently occurring errors
"""

import sqlite3
import re
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import math

from .database import DatabaseManager, LogEntry, LogSeverity

logger = logging.getLogger(__name__)


class SearchOperator(str, Enum):
    """
    🔧 SEARCH BUILDING BLOCKS - How to Combine Search Terms
    
    These are like the grammar rules for building complex searches.
    Just like you can say "find books by Shakespeare AND about love"
    or "find books about cats OR dogs", these operators let you
    build sophisticated search queries.
    """
    AND = "AND"         # 🤝 Both conditions must be true
    OR = "OR"           # 🔀 Either condition can be true  
    NOT = "NOT"         # 🚫 Exclude results matching this condition
    PHRASE = "PHRASE"   # 📝 Exact phrase match (words in exact order)
    WILDCARD = "*"      # 🌟 Partial matching (like "error*" finds "error", "errors", "errorMessage")


class SortOrder(str, Enum):
    """
    📊 RESULT ORGANIZATION - How to Order Search Results
    
    Like choosing how to sort books on a shelf - by title, author,
    publication date, or relevance to your search.
    """
    NEWEST_FIRST = "newest_first"       # 📅 Most recent errors first
    OLDEST_FIRST = "oldest_first"       # 📅 Oldest errors first  
    MOST_RELEVANT = "most_relevant"     # 🎯 Best matches first
    SEVERITY_HIGH = "severity_high"     # 🚨 Most critical errors first
    SEVERITY_LOW = "severity_low"       # ℹ️ Least critical errors first
    ALPHABETICAL = "alphabetical"       # 🔤 Alphabetical by content


@dataclass
class SearchQuery:
    """
    🎯 SEARCH REQUEST FORM - A Complete Search Request
    
    Think of this as a detailed library request form where you specify
    exactly what you're looking for using all available search options.
    Like filling out a form that says "I want books about X, published
    between Y and Z, by author A, that mention keywords B and C."
    """
    
    # 🔍 MAIN SEARCH TERMS
    text: Optional[str] = None                    # Main search text (searches content, summary, tags)
    exact_phrase: Optional[str] = None            # Exact phrase that must appear
    any_words: Optional[List[str]] = None         # Any of these words can match
    all_words: Optional[List[str]] = None         # All of these words must be present
    exclude_words: Optional[List[str]] = None     # None of these words should appear
    
    # 🗂️ CATEGORY FILTERS
    severities: Optional[List[LogSeverity]] = None    # Filter by error severity
    languages: Optional[List[str]] = None             # Filter by programming language
    tags: Optional[List[str]] = None                  # Filter by error tags
    projects: Optional[List[str]] = None              # Filter by project name
    sources: Optional[List[str]] = None               # Filter by log source
    
    # 📅 TIME FILTERS
    start_date: Optional[datetime] = None         # Earliest date to include
    end_date: Optional[datetime] = None           # Latest date to include  
    last_n_days: Optional[int] = None             # Only last N days
    last_n_hours: Optional[int] = None            # Only last N hours
    
    # 📊 RESULT CONTROL
    sort_by: SortOrder = SortOrder.NEWEST_FIRST   # How to order results
    limit: int = 100                              # Maximum results to return
    offset: int = 0                               # Results to skip (for pagination)
    
    # 🎛️ ADVANCED OPTIONS
    case_sensitive: bool = False                  # Should text search care about capitalization?
    include_archived: bool = False                # Include archived/old logs?
    similar_to_log_id: Optional[str] = None       # Find logs similar to this one


@dataclass
class SearchResult:
    """
    📋 SEARCH RESULTS PACKAGE - What We Found
    
    This is like the librarian's response when you make a search request.
    It includes not just the books you asked for, but also helpful
    information about the search itself - how many matches were found,
    how long it took, and suggestions for related searches.
    """
    
    # 📚 THE ACTUAL RESULTS
    logs: List[LogEntry]                          # The log entries that matched
    
    # 📊 SEARCH STATISTICS  
    total_matches: int                            # Total number of matching logs (may be more than returned)
    search_duration_ms: int                       # How long the search took
    query_executed: str                           # The actual database query that was run
    
    # 🎯 RESULT ANALYSIS
    match_quality_scores: Optional[List[float]] = None    # Relevance score for each result (0-1)
    highlighted_snippets: Optional[List[str]] = None      # Text snippets showing where matches occurred
    
    # 💡 SEARCH SUGGESTIONS
    suggested_filters: Optional[Dict[str, List[str]]] = None   # Suggested ways to refine the search
    related_tags: Optional[List[str]] = None                   # Tags that appear in results
    trending_terms: Optional[List[str]] = None                 # Popular search terms in your results


class SearchManager:
    """
    🔍 THE MASTER SEARCH LIBRARIAN - Finding Needles in Haystacks!
    
    Think of this class as the head research librarian who knows every
    search technique, every shortcut, and every way to find information
    in a massive collection. This librarian can:
    - Understand complex search requests in plain English
    - Use advanced indexing systems for lightning-fast searches
    - Suggest better search terms when you're not finding what you need
    - Find patterns and connections you might have missed
    - Remember what searches work well and optimize future searches
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like the librarian who's been working at the school for 20 years and
    knows exactly where everything is:
    - Ask for "books about World War 2" → instantly knows which section, authors, best resources
    - Ask for "that book with the blue cover about computers" → uses context clues to find it
    - Can suggest "students who liked that book also checked out these"
    - Knows which search terms work better than others
    - Can find information even when you don't describe it perfectly
    
    This SearchManager brings that level of expertise to finding error logs!
    """
    
    def __init__(self, database_manager: DatabaseManager):
        """
        🏗️ SETTING UP THE SEARCH DEPARTMENT
        
        When we create a new SearchManager, it's like setting up a new
        search department in the library with all the tools, indexes,
        and systems needed to handle complex search requests efficiently.
        """
        # 🗄️ CONNECTION TO THE MAIN DATABASE
        self.db = database_manager
        
        # 📚 SEARCH INDEXES FOR FAST LOOKUPS
        # Like specialized card catalogs that make searching faster
        self._text_index: Dict[str, Set[str]] = {}      # Word → Set of log IDs containing that word
        self._tag_index: Dict[str, Set[str]] = {}       # Tag → Set of log IDs with that tag
        self._bigram_index: Dict[str, Set[str]] = {}    # Two-word phrases → log IDs
        
        # 📊 SEARCH ANALYTICS
        self.search_history: List[Dict[str, Any]] = []  # Record of recent searches
        self.popular_terms: Dict[str, int] = {}         # Most searched terms
        self.max_history_size = 1000                    # Don't keep search history forever
        
        # ⚙️ SEARCH CONFIGURATION  
        self.config = {
            "enable_fuzzy_search": True,        # Allow approximate matching
            "enable_auto_suggest": True,        # Provide search suggestions
            "max_search_time_ms": 5000,         # Maximum time to spend on one search
            "index_rebuild_threshold": 1000,    # Rebuild indexes after this many new logs
            "highlight_context_chars": 200,     # Characters to show around search matches
        }
        
        # 🚀 INITIALIZE SEARCH INDEXES
        self._build_search_indexes()
        
        logger.info("Search manager initialized with full-text indexing")
    
    def _build_search_indexes(self):
        """
        📚 BUILDING THE LIBRARY'S CARD CATALOG SYSTEM
        
        This creates specialized indexes that make searching fast. It's like
        a librarian going through every book and creating multiple card
        catalogs: one sorted by title, one by author, one by subject,
        one by keywords that appear in the content.
        
        These indexes let us find results in milliseconds instead of minutes!
        """
        logger.info("Building search indexes...")
        start_time = datetime.now()
        
        # Clear existing indexes
        self._text_index.clear()
        self._tag_index.clear()
        self._bigram_index.clear()
        
        # Get all logs from database (in batches to avoid memory issues)
        batch_size = 1000
        offset = 0
        total_indexed = 0
        
        while True:
            # Get a batch of logs
            logs = self.db.search_logs(limit=batch_size, offset=offset)
            if not logs:
                break  # No more logs to process
            
            # Index each log in this batch
            for log in logs:
                self._index_log_content(log)
                total_indexed += 1
            
            offset += batch_size
        
        # Calculate indexing performance
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Search indexes built: {total_indexed} logs indexed in {duration:.2f}s")
        logger.info(f"Text index: {len(self._text_index)} terms")
        logger.info(f"Tag index: {len(self._tag_index)} tags") 
        logger.info(f"Bigram index: {len(self._bigram_index)} phrases")
    
    def _index_log_content(self, log: LogEntry):
        """
        📝 INDEXING ONE DOCUMENT - Adding to Our Card Catalog
        
        This takes one log entry and adds it to all our specialized indexes.
        Like a librarian processing a new book by adding cards to multiple
        card catalogs (title catalog, author catalog, subject catalog, etc.).
        """
        log_id = log.log_id
        
        # 🔤 INDEX ALL TEXT CONTENT
        # Combine all searchable text from the log
        searchable_text = " ".join(filter(None, [
            log.original_log,
            log.processed_log,
            log.summary,
            log.project_name,
            log.file_path
        ]))
        
        # Extract individual words and add to text index
        words = self._extract_words(searchable_text)
        for word in words:
            if word not in self._text_index:
                self._text_index[word] = set()
            self._text_index[word].add(log_id)
        
        # 🏷️ INDEX TAGS
        for tag in log.tags:
            tag_lower = tag.lower()
            if tag_lower not in self._tag_index:
                self._tag_index[tag_lower] = set()
            self._tag_index[tag_lower].add(log_id)
        
        # 📝 INDEX WORD PAIRS (BIGRAMS) for phrase searching
        # This helps with searches like "index error" or "connection timeout"
        bigrams = self._extract_bigrams(words)
        for bigram in bigrams:
            if bigram not in self._bigram_index:
                self._bigram_index[bigram] = set()
            self._bigram_index[bigram].add(log_id)
    
    def _extract_words(self, text: str) -> List[str]:
        """
        🔤 BREAKING TEXT INTO SEARCHABLE WORDS
        
        This takes a chunk of text and breaks it down into individual words
        that can be searched. Like a librarian creating individual index
        cards for every important word in a book's title and content.
        """
        if not text:
            return []
        
        # Convert to lowercase for case-insensitive searching
        text = text.lower()
        
        # Extract words (letters, numbers, underscores)
        # This regex finds programming-friendly words like "IndexError" or "user_name"
        words = re.findall(r'\b\w+\b', text)
        
        # Remove very short words (less than 2 characters) and very common words
        stopwords = {'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'the', 'is', 'was', 'are', 'were'}
        words = [word for word in words if len(word) >= 2 and word not in stopwords]
        
        return words
    
    def _extract_bigrams(self, words: List[str]) -> List[str]:
        """
        📝 CREATING TWO-WORD PHRASES FOR BETTER SEARCH
        
        This creates pairs of adjacent words, which helps with phrase
        searching. Like indexing both "connection" and "timeout" separately,
        but also indexing "connection timeout" as a phrase.
        """
        if len(words) < 2:
            return []
        
        bigrams = []
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            bigrams.append(bigram)
        
        return bigrams
    
    async def search(self, query: SearchQuery) -> SearchResult:
        """
        🔍 THE MASTER SEARCH FUNCTION - Finding What You Need!
        
        This is the main search function that handles any type of search
        request. Think of it as the master librarian who can handle any
        research question, no matter how simple or complex.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like going to the reference desk with any kind of research question:
        - "I need information about Python errors" (simple keyword search)
        - "Find all critical errors from last week that mention 'database'" (complex filtered search)
        - "Show me errors similar to this one I had yesterday" (similarity search)
        - "What are the most common JavaScript problems this month?" (analytical search)
        
        The librarian knows how to handle all these different types of requests!
        """
        start_time = datetime.now()
        logger.debug(f"Executing search query: {query}")
        
        try:
            # 🎯 BUILD THE DATABASE QUERY based on search criteria
            sql_query, params = self._build_sql_query(query)
            
            # ⚡ EXECUTE THE SEARCH using our optimized database query
            with sqlite3.connect(self.db.database_path) as conn:
                cursor = conn.execute(sql_query, params)
                rows = cursor.fetchall()
            
            # 🔄 CONVERT DATABASE ROWS TO LOG ENTRIES
            logs = []
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
                logs.append(log_entry)
            
            # 📊 CALCULATE SEARCH STATISTICS
            total_matches = len(logs)  # For now, assume we got all matches
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # 🎯 APPLY POST-PROCESSING (relevance scoring, highlighting, etc.)
            if query.text or query.exact_phrase:
                match_scores = self._calculate_relevance_scores(logs, query)
                highlighted_snippets = self._generate_highlights(logs, query)
            else:
                match_scores = None
                highlighted_snippets = None
            
            # 💡 GENERATE SEARCH SUGGESTIONS
            suggested_filters = self._generate_filter_suggestions(logs)
            related_tags = self._extract_related_tags(logs)
            
            # 📝 RECORD THIS SEARCH for analytics
            self._record_search(query, total_matches, duration_ms)
            
            # 📦 PACKAGE UP THE RESULTS
            result = SearchResult(
                logs=logs,
                total_matches=total_matches,
                search_duration_ms=duration_ms,
                query_executed=sql_query,
                match_quality_scores=match_scores,
                highlighted_snippets=highlighted_snippets,
                suggested_filters=suggested_filters,
                related_tags=related_tags,
                trending_terms=self._get_trending_terms()
            )
            
            logger.debug(f"Search completed: {total_matches} results in {duration_ms}ms")
            return result
            
        except Exception as e:
            # ❌ SEARCH ERROR - something went wrong during search
            logger.error(f"Search failed: {e}")
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Return empty results with error information
            return SearchResult(
                logs=[],
                total_matches=0,
                search_duration_ms=duration_ms,
                query_executed=f"ERROR: {str(e)}",
                match_quality_scores=None,
                highlighted_snippets=None,
                suggested_filters=None,
                related_tags=None,
                trending_terms=None
            )
    
    def _build_sql_query(self, query: SearchQuery) -> Tuple[str, List[Any]]:
        """
        🏗️ BUILDING THE DATABASE SEARCH QUERY
        
        This converts our high-level search request into the specific
        database language (SQL) that can actually find the data.
        Like translating "find books about dogs" into the library's
        computer system language.
        """
        # Start with base query
        sql = """
            SELECT log_id, timestamp, original_log, processed_log, summary,
                   tags, severity, language, metadata, project_name, file_path, source
            FROM logs
            WHERE 1=1
        """
        params = []
        
        # 📅 TIME FILTERS
        if query.start_date:
            sql += " AND timestamp >= ?"
            params.append(query.start_date)
        if query.end_date:
            sql += " AND timestamp <= ?"
            params.append(query.end_date)
        if query.last_n_days:
            cutoff = datetime.now() - timedelta(days=query.last_n_days)
            sql += " AND timestamp >= ?"
            params.append(cutoff)
        if query.last_n_hours:
            cutoff = datetime.now() - timedelta(hours=query.last_n_hours)
            sql += " AND timestamp >= ?"
            params.append(cutoff)
        
        # 🌡️ SEVERITY FILTERS
        if query.severities:
            severity_placeholders = ','.join(['?'] * len(query.severities))
            sql += f" AND severity IN ({severity_placeholders})"
            params.extend([sev.value for sev in query.severities])
        
        # 💻 LANGUAGE FILTERS
        if query.languages:
            lang_placeholders = ','.join(['?'] * len(query.languages))
            sql += f" AND language IN ({lang_placeholders})"
            params.extend(query.languages)
        
        # 📁 PROJECT FILTERS
        if query.projects:
            proj_placeholders = ','.join(['?'] * len(query.projects))
            sql += f" AND project_name IN ({proj_placeholders})"
            params.extend(query.projects)
        
        # 🌐 SOURCE FILTERS
        if query.sources:
            source_placeholders = ','.join(['?'] * len(query.sources))
            sql += f" AND source IN ({source_placeholders})"
            params.extend(query.sources)
        
        # 🔍 TEXT SEARCH
        if query.text:
            # Search in multiple text fields
            text_search = f"%{query.text}%"
            sql += """ AND (
                original_log LIKE ? OR 
                processed_log LIKE ? OR 
                summary LIKE ? OR
                project_name LIKE ? OR
                file_path LIKE ?
            )"""
            params.extend([text_search] * 5)
        
        # 📝 EXACT PHRASE SEARCH
        if query.exact_phrase:
            phrase_search = f"%{query.exact_phrase}%"
            sql += """ AND (
                original_log LIKE ? OR 
                processed_log LIKE ? OR 
                summary LIKE ?
            )"""
            params.extend([phrase_search] * 3)
        
        # 🏷️ TAG FILTERS
        if query.tags:
            tag_conditions = []
            for tag in query.tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")
            sql += f" AND ({' OR '.join(tag_conditions)})"
        
        # 📊 SORTING
        if query.sort_by == SortOrder.NEWEST_FIRST:
            sql += " ORDER BY timestamp DESC"
        elif query.sort_by == SortOrder.OLDEST_FIRST:
            sql += " ORDER BY timestamp ASC"
        elif query.sort_by == SortOrder.SEVERITY_HIGH:
            # Custom ordering for severity (critical first, then error, warning, etc.)
            sql += """ ORDER BY 
                CASE severity 
                    WHEN 'critical' THEN 1
                    WHEN 'error' THEN 2  
                    WHEN 'warning' THEN 3
                    WHEN 'info' THEN 4
                    WHEN 'debug' THEN 5
                    WHEN 'trace' THEN 6
                    ELSE 7
                END, timestamp DESC"""
        elif query.sort_by == SortOrder.ALPHABETICAL:
            sql += " ORDER BY original_log ASC"
        else:
            sql += " ORDER BY timestamp DESC"  # Default to newest first
        
        # 📏 LIMIT AND OFFSET
        sql += " LIMIT ? OFFSET ?"
        params.extend([query.limit, query.offset])
        
        return sql, params
    
    def _calculate_relevance_scores(self, logs: List[LogEntry], query: SearchQuery) -> List[float]:
        """
        🎯 SCORING SEARCH RESULTS - How Well Do They Match?
        
        This calculates a relevance score for each search result to help
        rank them by how well they match what you're looking for.
        Like a librarian saying "this book is exactly what you want,
        this one is pretty close, and this one is somewhat related."
        """
        scores = []
        search_terms = []
        
        # Extract search terms from query
        if query.text:
            search_terms.extend(self._extract_words(query.text))
        if query.exact_phrase:
            search_terms.extend(self._extract_words(query.exact_phrase))
        if query.all_words:
            search_terms.extend(query.all_words)
        if query.any_words:
            search_terms.extend(query.any_words)
        
        if not search_terms:
            # No text search terms, return equal scores
            return [1.0] * len(logs)
        
        for log in logs:
            score = self._calculate_log_relevance(log, search_terms)
            scores.append(score)
        
        return scores
    
    def _calculate_log_relevance(self, log: LogEntry, search_terms: List[str]) -> float:
        """
        🎯 HOW WELL DOES THIS LOG MATCH THE SEARCH?
        
        This calculates a relevance score (0.0 to 1.0) for one log entry
        based on how many search terms it contains and where they appear.
        """
        if not search_terms:
            return 1.0
        
        # Combine all searchable text
        searchable_text = " ".join(filter(None, [
            log.original_log,
            log.processed_log,
            log.summary,
            " ".join(log.tags)  # Tags are important for relevance
        ])).lower()
        
        if not searchable_text:
            return 0.0
        
        # Count how many search terms appear in the text
        matches = 0
        total_terms = len(search_terms)
        
        for term in search_terms:
            term_lower = term.lower()
            if term_lower in searchable_text:
                matches += 1
                
                # Bonus points for exact matches in summary (summary is most important)
                if log.summary and term_lower in log.summary.lower():
                    matches += 0.5
                
                # Bonus points for matches in tags (tags are curated/important)
                tag_text = " ".join(log.tags).lower()
                if term_lower in tag_text:
                    matches += 0.3
        
        # Calculate final score
        if total_terms == 0:
            return 1.0
        
        base_score = matches / total_terms
        return min(1.0, base_score)  # Cap at 1.0
    
    def _generate_highlights(self, logs: List[LogEntry], query: SearchQuery) -> List[str]:
        """
        ✨ HIGHLIGHTING SEARCH MATCHES - Showing Where We Found Things
        
        This creates text snippets that show exactly where the search terms
        were found in each log, with the matching words highlighted.
        Like showing you the exact paragraph in a book where your search
        term appears, with the words highlighted in yellow.
        """
        highlights = []
        search_terms = []
        
        # Extract search terms
        if query.text:
            search_terms.extend(self._extract_words(query.text))
        if query.exact_phrase:
            search_terms.extend(self._extract_words(query.exact_phrase))
        
        for log in logs:
            highlight = self._create_highlight_snippet(log, search_terms)
            highlights.append(highlight)
        
        return highlights
    
    def _create_highlight_snippet(self, log: LogEntry, search_terms: List[str]) -> str:
        """
        ✨ CREATING ONE HIGHLIGHTED SNIPPET
        
        This finds the best place in the log where search terms appear
        and creates a short snippet with the matching words highlighted.
        """
        if not search_terms:
            # No search terms, return beginning of log
            text = log.processed_log or log.original_log
            if len(text) > self.config["highlight_context_chars"]:
                return text[:self.config["highlight_context_chars"]] + "..."
            return text
        
        # Find the best snippet that contains the most search terms
        text = log.processed_log or log.original_log
        if not text:
            return "No content available"
        
        # Simple implementation: find first occurrence of any search term
        text_lower = text.lower()
        best_position = 0
        
        for term in search_terms:
            term_lower = term.lower()
            pos = text_lower.find(term_lower)
            if pos >= 0:
                best_position = pos
                break
        
        # Extract context around the match
        context_chars = self.config["highlight_context_chars"]
        start = max(0, best_position - context_chars // 2)
        end = min(len(text), start + context_chars)
        
        snippet = text[start:end]
        
        # Add ellipsis if we're not at the beginning/end
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        # TODO: Add actual highlighting markup (like <mark>term</mark>)
        # For now, return the snippet as-is
        return snippet
    
    def _generate_filter_suggestions(self, logs: List[LogEntry]) -> Dict[str, List[str]]:
        """
        💡 SUGGESTING WAYS TO REFINE THE SEARCH
        
        This analyzes the search results and suggests filters that might
        help narrow down the results. Like a librarian saying "I found
        50 books about programming - would you like to focus on Python
        books, or books from the last 5 years?"
        """
        if not logs:
            return {}
        
        suggestions = {}
        
        # Suggest languages that appear in results
        languages = {}
        for log in logs:
            lang = log.language
            languages[lang] = languages.get(lang, 0) + 1
        
        if len(languages) > 1:  # Only suggest if there are multiple languages
            # Sort by frequency and take top 5
            top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
            suggestions["languages"] = [lang for lang, count in top_languages]
        
        # Suggest severities that appear in results
        severities = {}
        for log in logs:
            sev = log.severity.value
            severities[sev] = severities.get(sev, 0) + 1
        
        if len(severities) > 1:
            top_severities = sorted(severities.items(), key=lambda x: x[1], reverse=True)[:3]
            suggestions["severities"] = [sev for sev, count in top_severities]
        
        # Suggest projects that appear in results
        projects = {}
        for log in logs:
            if log.project_name:
                proj = log.project_name
                projects[proj] = projects.get(proj, 0) + 1
        
        if len(projects) > 1:
            top_projects = sorted(projects.items(), key=lambda x: x[1], reverse=True)[:5]
            suggestions["projects"] = [proj for proj, count in top_projects]
        
        return suggestions
    
    def _extract_related_tags(self, logs: List[LogEntry]) -> List[str]:
        """
        🏷️ FINDING RELATED ERROR CATEGORIES
        
        This looks at all the tags in the search results and identifies
        the most common ones. These can help users understand what types
        of errors they're dealing with.
        """
        tag_counts = {}
        
        for log in logs:
            for tag in log.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Return top 10 most common tags
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        return [tag for tag, count in sorted_tags]
    
    def _get_trending_terms(self) -> List[str]:
        """
        📈 WHAT ARE PEOPLE SEARCHING FOR LATELY?
        
        This returns the most popular search terms from recent searches,
        which can help users discover what issues are trending.
        """
        # Return top 10 most searched terms
        sorted_terms = sorted(self.popular_terms.items(), key=lambda x: x[1], reverse=True)[:10]
        return [term for term, count in sorted_terms]
    
    def _record_search(self, query: SearchQuery, result_count: int, duration_ms: int):
        """
        📝 RECORDING SEARCH ANALYTICS
        
        This keeps track of what people are searching for to help
        improve the search system and provide better suggestions.
        """
        # Record the search in our history
        search_record = {
            "timestamp": datetime.now(),
            "query_text": query.text,
            "result_count": result_count,
            "duration_ms": duration_ms,
            "filters_used": {
                "severities": len(query.severities) if query.severities else 0,
                "languages": len(query.languages) if query.languages else 0,
                "time_filter": bool(query.start_date or query.end_date or query.last_n_days),
            }
        }
        
        self.search_history.append(search_record)
        
        # Keep history from growing too large
        if len(self.search_history) > self.max_history_size:
            self.search_history.pop(0)
        
        # Update popular terms
        if query.text:
            terms = self._extract_words(query.text)
            for term in terms:
                self.popular_terms[term] = self.popular_terms.get(term, 0) + 1
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """
        📊 SEARCH SYSTEM ANALYTICS
        
        This provides insights into how the search system is being used,
        what searches are most common, and how well the system is performing.
        """
        if not self.search_history:
            return {"message": "No search history available"}
        
        recent_searches = self.search_history[-100:]  # Last 100 searches
        
        # Calculate average search time
        total_time = sum(search["duration_ms"] for search in recent_searches)
        avg_time = total_time / len(recent_searches) if recent_searches else 0
        
        # Find most common result counts
        result_counts = [search["result_count"] for search in recent_searches]
        avg_results = sum(result_counts) / len(result_counts) if result_counts else 0
        
        return {
            "total_searches": len(self.search_history),
            "recent_searches": len(recent_searches),
            "average_search_time_ms": round(avg_time, 2),
            "average_results_per_search": round(avg_results, 2),
            "popular_search_terms": self._get_trending_terms(),
            "index_stats": {
                "text_terms": len(self._text_index),
                "tags": len(self._tag_index),
                "bigrams": len(self._bigram_index)
            }
        }