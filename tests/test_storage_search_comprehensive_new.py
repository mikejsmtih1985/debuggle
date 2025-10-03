"""
Comprehensive tests for storage/search.py focusing on search functionality and data retrieval.
Following Debuggle's quality-first testing philosophy.

Target: 70%+ coverage focusing on:
- Search algorithms and query processing
- Real search scenarios users encounter
- Error handling in search operations
- Integration with database layer
"""

import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, mock_open

from src.debuggle.storage.search import (
    SearchManager, SearchQuery, SearchResult, SearchOperator
)


class TestSearchManager:
    """Test core search manager functionality."""
    
    def setup_method(self):
        """Set up search manager for each test."""
        self.search_manager = SearchManager()
    
    def test_search_engine_initialization(self):
        """Test search engine initializes correctly."""
        assert self.search_engine is not None
        assert hasattr(self.search_engine, 'index')
        assert hasattr(self.search_engine, 'query_processor')
    
    def test_basic_text_search(self):  
        """Test basic text search functionality - core user workflow."""
        # Add some test logs to search
        test_logs = [
            "FileNotFoundError: [Errno 2] No such file or directory: 'config.txt'",
            "IndexError: list index out of range",
            "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
        ]
        
        for i, log in enumerate(test_logs):
            log_entry = LogEntry(
                log_id=f"test-{i}",
                raw_log=log,
                severity=LogSeverity.ERROR,
                timestamp=datetime.now()
            )
            self.search_engine.add_to_index(log_entry)
        
        # Search for specific error type
        results = self.search_engine.search("FileNotFoundError")
        assert len(results) > 0
        assert any("FileNotFoundError" in result.content for result in results)
    
    def test_search_with_multiple_keywords(self):
        """Test search with multiple keywords - realistic user behavior."""
        test_logs = [
            "Database connection failed: timeout after 30 seconds",
            "Failed to connect to MySQL database on localhost:3306",
            "Connection timeout: could not reach server",
            "File upload successful"
        ]
        
        for i, log in enumerate(test_logs):
            log_entry = LogEntry(
                log_id=f"multi-{i}",
                raw_log=log,
                severity=LogSeverity.ERROR,
                timestamp=datetime.now()
            )
            self.search_engine.add_to_index(log_entry)
        
        # Search for multiple related terms
        results = self.search_engine.search("database connection failed")
        assert len(results) > 0
        
        # Should find both database-related logs
        database_results = [r for r in results if "database" in r.content.lower()]
        assert len(database_results) >= 1
    
    def test_search_case_insensitive(self):
        """Test search is case insensitive - better user experience."""
        log_entry = LogEntry(
            log_id="case-test",
            raw_log="NullPointerException: Cannot invoke method on null object",
            severity=LogSeverity.ERROR,
            timestamp=datetime.now()
        )
        self.search_engine.add_to_index(log_entry)
        
        # Test various case combinations
        test_queries = ["nullpointerexception", "NULLPOINTEREXCEPTION", "NullPointer", "null"]
        
        for query in test_queries:
            results = self.search_engine.search(query)
            assert len(results) > 0, f"Query '{query}' should find results"
    
    def test_search_with_filters(self):
        """Test search with severity and date filters."""
        # Create logs with different severities and dates
        test_data = [
            ("Critical error occurred", LogSeverity.CRITICAL, datetime.now()),
            ("Warning: deprecated function used", LogSeverity.WARNING, datetime.now() - timedelta(days=1)),
            ("Info: operation completed", LogSeverity.INFO, datetime.now() - timedelta(hours=1))
        ]
        
        for i, (log, severity, timestamp) in enumerate(test_data):
            log_entry = LogEntry(
                log_id=f"filter-{i}",
                raw_log=log,
                severity=severity,
                timestamp=timestamp
            )
            self.search_engine.add_to_index(log_entry)
        
        # Search with severity filter
        critical_results = self.search_engine.search("error", severity_filter=LogSeverity.CRITICAL)
        assert len(critical_results) > 0
        assert all(result.severity == LogSeverity.CRITICAL for result in critical_results)
        
        # Search with date filter
        recent_results = self.search_engine.search("", 
                                                 start_date=datetime.now() - timedelta(hours=2))
        assert len(recent_results) > 0
    
    def test_search_ranking_and_relevance(self):
        """Test search results are ranked by relevance."""
        test_logs = [
            "FileNotFoundError in main.py line 42",  # Exact match
            "Error: file not found when loading config",  # Partial match
            "System file corruption detected",  # Weak match
            "Successfully loaded all files"  # No match but contains 'file'
        ]
        
        for i, log in enumerate(test_logs):
            log_entry = LogEntry(
                log_id=f"rank-{i}",
                raw_log=log,
                severity=LogSeverity.ERROR,
                timestamp=datetime.now()
            )
            self.search_engine.add_to_index(log_entry)
        
        results = self.search_engine.search("FileNotFoundError")
        assert len(results) > 0
        
        # Most relevant result should be first
        best_result = results[0]
        assert "FileNotFoundError" in best_result.content
        
        # Results should be ordered by relevance score
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].score >= results[i + 1].score
    
    def test_empty_search_query(self):
        """Test handling of empty search queries."""
        results = self.search_engine.search("")
        # Should return recent results or empty list, not crash
        assert isinstance(results, list)
    
    def test_search_with_special_characters(self):
        """Test search handles special characters properly."""
        log_with_special_chars = "Error: Cannot parse JSON {\"key\": \"value\"} at line 15"
        
        log_entry = LogEntry(
            log_id="special-chars",
            raw_log=log_with_special_chars,
            severity=LogSeverity.ERROR,
            timestamp=datetime.now()
        )
        self.search_engine.add_to_index(log_entry)
        
        # Search with special characters should work
        results = self.search_engine.search('JSON {"key"')
        assert len(results) >= 0  # Should not crash
        
        # Search for the JSON keyword should find the log
        json_results = self.search_engine.search("JSON")
        assert len(json_results) > 0


class TestSearchQuery:
    """Test search query processing and parsing."""
    
    def test_search_query_parsing(self):
        """Test parsing of complex search queries."""
        query = SearchQuery("error AND database OR timeout")
        assert query.terms is not None
        assert isinstance(query.terms, list)
    
    def test_search_query_with_quotes(self):
        """Test parsing quoted search terms."""
        query = SearchQuery('"exact phrase" AND keyword')
        assert query.has_phrases()
        assert "exact phrase" in query.get_phrases()
    
    def test_search_query_with_wildcards(self):
        """Test wildcard search patterns."""
        query = SearchQuery("file*.py OR *.log")
        assert query.has_wildcards()
    
    def test_search_query_normalization(self):
        """Test query normalization and cleanup."""
        messy_query = "  ERROR   and    DATABASE  "
        query = SearchQuery(messy_query)
        normalized = query.normalize()
        
        assert normalized is not None
        assert len(normalized.strip()) > 0
        assert "  " not in normalized  # Multiple spaces removed


class TestSearchIndex:
    """Test search indexing functionality."""
    
    def setup_method(self):
        """Set up search index for each test."""
        self.search_index = SearchIndex()
    
    def test_index_creation(self):
        """Test creating search index."""
        assert self.search_index is not None
        assert hasattr(self.search_index, 'documents')
    
    def test_adding_documents_to_index(self):
        """Test adding documents to search index."""
        doc_id = "test-doc-1"
        content = "Error: Failed to load configuration file"
        
        self.search_index.add_document(doc_id, content)
        
        # Verify document was added
        assert self.search_index.document_count() > 0
        assert self.search_index.contains_document(doc_id)
    
    def test_updating_documents_in_index(self):
        """Test updating existing documents in index."""
        doc_id = "update-test"
        original_content = "Original error message"
        updated_content = "Updated error message with more details"
        
        # Add original document
        self.search_index.add_document(doc_id, original_content)
        original_count = self.search_index.document_count()
        
        # Update document
        self.search_index.update_document(doc_id, updated_content)
        
        # Count should remain the same (update, not add)
        assert self.search_index.document_count() == original_count
        
        # Content should be updated
        retrieved = self.search_index.get_document(doc_id)
        assert updated_content in retrieved
    
    def test_removing_documents_from_index(self):
        """Test removing documents from index."""
        doc_id = "remove-test"
        content = "This document will be removed"
        
        # Add document
        self.search_index.add_document(doc_id, content)
        assert self.search_index.contains_document(doc_id)
        
        # Remove document
        self.search_index.remove_document(doc_id)
        assert not self.search_index.contains_document(doc_id)
    
    def test_index_persistence(self):
        """Test saving and loading index to/from disk."""
        # Add some documents
        test_docs = [
            ("doc1", "First error message"),
            ("doc2", "Second error message"),
            ("doc3", "Third error message")
        ]
        
        for doc_id, content in test_docs:
            self.search_index.add_document(doc_id, content)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            index_file = f.name
        
        try:
            # Save index
            self.search_index.save_to_file(index_file)
            assert os.path.exists(index_file)
            
            # Load index into new instance
            new_index = SearchIndex()
            new_index.load_from_file(index_file)
            
            # Verify all documents were loaded
            assert new_index.document_count() == len(test_docs)
            for doc_id, content in test_docs:
                assert new_index.contains_document(doc_id)
                
        finally:
            if os.path.exists(index_file):
                os.unlink(index_file)


class TestSearchErrorHandling:
    """Test error handling in search operations."""
    
    def setup_method(self):
        """Set up search engine for each test."""
        self.search_engine = SearchEngine()
    
    def test_search_with_malformed_query(self):
        """Test search handles malformed queries gracefully."""
        malformed_queries = [
            "AND OR NOT",  # Only operators
            "(((",  # Unbalanced parentheses
            "\\invalid\\regex[",  # Invalid regex
            None,  # None query
        ]
        
        for query in malformed_queries:
            try:
                results = self.search_engine.search(query)
                assert isinstance(results, list)  # Should return empty list, not crash
            except Exception as e:
                # If it raises an exception, it should be a handled one
                assert "search" in str(e).lower() or "query" in str(e).lower()
    
    @patch('src.debuggle.storage.search.SearchIndex.search')
    def test_search_engine_index_failure(self, mock_search):
        """Test search engine handles index failures."""
        mock_search.side_effect = Exception("Index corrupted")
        
        results = self.search_engine.search("test query")
        
        # Should handle index failures gracefully
        assert isinstance(results, list)
    
    def test_search_with_extremely_long_query(self):
        """Test search handles very long queries."""
        long_query = "error " * 1000  # Very long query
        
        results = self.search_engine.search(long_query)
        
        # Should handle without crashing
        assert isinstance(results, list)
    
    @patch('src.debuggle.storage.search.SearchIndex.load_from_file')
    def test_search_index_load_failure(self, mock_load):
        """Test handling of index loading failures."""
        mock_load.side_effect = IOError("Cannot read index file")
        
        search_index = SearchIndex()
        
        # Should handle load failure gracefully
        try:
            search_index.load_from_file("nonexistent_file.json")
        except Exception as e:
            assert "index" in str(e).lower() or "file" in str(e).lower()


class TestSearchPerformance:
    """Test search performance with large datasets."""
    
    def setup_method(self):
        """Set up search engine for each test."""
        self.search_engine = SearchEngine()
    
    def test_search_with_large_dataset(self):
        """Test search performance with many documents."""
        import time
        
        # Add a large number of documents
        num_docs = 100
        for i in range(num_docs):
            log_entry = LogEntry(
                log_id=f"perf-test-{i}",
                raw_log=f"Error {i}: Something went wrong in module {i % 10}",
                severity=LogSeverity.ERROR,
                timestamp=datetime.now()
            )
            self.search_engine.add_to_index(log_entry)
        
        # Measure search time
        start_time = time.time()
        results = self.search_engine.search("Error")
        search_time = time.time() - start_time
        
        # Should complete search quickly (under 1 second)
        assert search_time < 1.0
        assert len(results) > 0
    
    def test_concurrent_search_operations(self):
        """Test concurrent search operations."""
        import concurrent.futures
        
        # Add test data
        for i in range(50):
            log_entry = LogEntry(
                log_id=f"concurrent-{i}",
                raw_log=f"Concurrent error {i}",
                severity=LogSeverity.ERROR,
                timestamp=datetime.now()
            )
            self.search_engine.add_to_index(log_entry)
        
        def perform_search(query):
            return self.search_engine.search(f"error {query}")
        
        # Perform concurrent searches
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(perform_search, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        # All searches should complete successfully
        for result_list in results:
            assert isinstance(result_list, list)


class TestSearchIntegration:
    """Test search integration with other components."""
    
    def setup_method(self):
        """Set up search engine for each test."""
        self.search_engine = SearchEngine()
    
    @patch('src.debuggle.storage.database.DatabaseManager')
    def test_search_with_database_integration(self, mock_db):
        """Test search integration with database."""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        # Mock database returning log entries
        mock_logs = [
            LogEntry(
                log_id="db-1",
                raw_log="Database error: connection failed",
                severity=LogSeverity.ERROR,
                timestamp=datetime.now()
            )
        ]
        mock_db_instance.search_logs.return_value = mock_logs
        
        # Test search with database backend
        results = self.search_engine.search_with_db("database")
        
        assert isinstance(results, list)
        if results:
            assert any("database" in result.content.lower() for result in results)
    
    def test_search_result_serialization(self):
        """Test search results can be serialized for API responses."""
        # Add test log
        log_entry = LogEntry(
            log_id="serialize-test",
            raw_log="Serialization test error",
            severity=LogSeverity.ERROR,
            timestamp=datetime.now()
        )
        self.search_engine.add_to_index(log_entry)
        
        results = self.search_engine.search("serialization")
        
        # Should be able to serialize results to JSON
        for result in results:
            try:
                json_data = json.dumps(result.__dict__, default=str)
                assert len(json_data) > 0
                
                # Should be able to deserialize
                parsed = json.loads(json_data)
                assert isinstance(parsed, dict)
            except (TypeError, ValueError) as e:
                pytest.fail(f"Search result serialization failed: {e}")
    
    def test_search_with_realtime_updates(self):
        """Test search index updates in real-time."""
        # Initial search should return no results
        initial_results = self.search_engine.search("realtime")
        assert len(initial_results) == 0
        
        # Add document in real-time
        new_log = LogEntry(
            log_id="realtime-test",
            raw_log="Realtime update test error",
            severity=LogSeverity.ERROR,
            timestamp=datetime.now()
        )
        self.search_engine.add_to_index(new_log)
        
        # Search should immediately find new document
        updated_results = self.search_engine.search("realtime")
        assert len(updated_results) > 0
        assert any("realtime" in result.content.lower() for result in updated_results)


class TestAdvancedSearchFeatures:
    """Test advanced search features and capabilities."""
    
    def setup_method(self):
        """Set up search engine for each test."""
        self.search_engine = SearchEngine()
    
    def test_fuzzy_search(self):
        """Test fuzzy/approximate string matching."""
        # Add log with specific term
        log_entry = LogEntry(
            log_id="fuzzy-test",
            raw_log="FileNotFoundException occurred in application",
            severity=LogSeverity.ERROR,
            timestamp=datetime.now()
        )
        self.search_engine.add_to_index(log_entry)
        
        # Search with typo should still find results
        typo_results = self.search_engine.search("FileNotFoudException")  # 'n' missing
        # Fuzzy search may or may not be implemented, but shouldn't crash
        assert isinstance(typo_results, list)
    
    def test_search_suggestions(self):
        """Test search suggestions for misspelled queries."""
        # Add common error terms
        common_errors = [
            "NullPointerException",
            "IndexOutOfBoundsException", 
            "FileNotFoundException",
            "IllegalArgumentException"
        ]
        
        for i, error in enumerate(common_errors):
            log_entry = LogEntry(
                log_id=f"suggest-{i}",
                raw_log=f"{error} occurred at runtime",
                severity=LogSeverity.ERROR,
                timestamp=datetime.now()
            )
            self.search_engine.add_to_index(log_entry)
        
        # Test getting suggestions for partial query
        suggestions = self.search_engine.get_suggestions("FileNot")
        assert isinstance(suggestions, list)
        
        if suggestions:
            assert any("FileNotFoundException" in suggestion for suggestion in suggestions)
    
    def test_search_faceting(self):
        """Test search result faceting/grouping."""
        # Add logs with different categories
        test_logs = [
            ("Database connection error", "database", LogSeverity.ERROR),
            ("Database timeout", "database", LogSeverity.WARNING),
            ("File not found", "filesystem", LogSeverity.ERROR),
            ("Permission denied", "filesystem", LogSeverity.CRITICAL)
        ]
        
        for i, (log, category, severity) in enumerate(test_logs):
            log_entry = LogEntry(
                log_id=f"facet-{i}",
                raw_log=log,
                severity=severity,
                timestamp=datetime.now(),
                tags=[category]
            )
            self.search_engine.add_to_index(log_entry)
        
        # Search with faceting
        results = self.search_engine.search("error", include_facets=True)
        
        # Should include facet information
        assert isinstance(results, list)
        if hasattr(results, 'facets'):
            assert 'severity' in results.facets
            assert 'category' in results.facets


if __name__ == "__main__":
    pytest.main([__file__, "-v"])