"""
Coverage handling plugin for graceful test failures.
"""
import pytest
from typing import Dict, Any


def pytest_configure(config):
    """Configure pytest with coverage handling."""
    config.addinivalue_line(
        "markers", "coverage_required: mark test as requiring minimum coverage"
    )


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Handle coverage failures gracefully with informative messages."""
    if exitstatus == 1 and hasattr(terminalreporter, 'config'):
        # Check if this was a coverage failure
        coverage_reports = []
        for line in terminalreporter._get_main_color():
            if "Coverage failure" in str(line):
                coverage_reports.append(line)
        
        if coverage_reports:
            terminalreporter.write_sep("=", "COVERAGE IMPROVEMENT GUIDANCE", yellow=True)
            terminalreporter.write_line("")
            terminalreporter.write_line("❌ Test coverage below required threshold!")
            terminalreporter.write_line("")
            terminalreporter.write_line("🎯 HOW TO IMPROVE COVERAGE:")
            terminalreporter.write_line("  1. Run: pytest --cov-report=html to see detailed coverage report")
            terminalreporter.write_line("  2. Open: htmlcov/index.html in your browser")
            terminalreporter.write_line("  3. Focus on files with 0% coverage first")
            terminalreporter.write_line("  4. Add tests for critical business logic")
            terminalreporter.write_line("")
            terminalreporter.write_line("📊 PRIORITY ORDER FOR ADDING TESTS:")
            terminalreporter.write_line("  • Core functionality (processor.py, analyzer.py)")
            terminalreporter.write_line("  • Configuration and utilities")
            terminalreporter.write_line("  • Error handling and edge cases")
            terminalreporter.write_line("  • Integration scenarios")
            terminalreporter.write_line("")
            terminalreporter.write_line("💡 QUICK WINS:")
            terminalreporter.write_line("  • Test simple functions and classes first")
            terminalreporter.write_line("  • Add validation tests for models")
            terminalreporter.write_line("  • Test error conditions and exceptions")
            terminalreporter.write_line("")


class CoverageHelper:
    """Helper class for managing test coverage expectations."""
    
    @staticmethod
    def get_coverage_targets() -> Dict[str, int]:
        """Define coverage targets for different modules."""
        return {
            "models.py": 95,           # Data models should be highly tested
            "config_v2.py": 80,       # Configuration is critical
            "processor.py": 75,       # Core business logic
            "context_extractor.py": 70,  # Important functionality
            "core/": 65,              # Core modules
            "utils/": 60,             # Utility functions
            "storage/": 50,           # Database layer (harder to test)
        }
    
    @staticmethod
    def suggest_tests_for_module(module_name: str) -> list:
        """Suggest what tests to add for a specific module."""
        suggestions = {
            "models.py": [
                "Test all validation rules",
                "Test edge cases for field constraints",
                "Test serialization/deserialization",
                "Test error handling for invalid data"
            ],
            "config_v2.py": [
                "Test environment variable loading",
                "Test default value assignments",
                "Test validation rules",
                "Test different environment configurations"
            ],
            "processor.py": [
                "Test log processing pipeline",
                "Test error detection algorithms",
                "Test language detection",
                "Test output formatting"
            ],
            "context_extractor.py": [
                "Test context extraction logic",
                "Test file parsing",
                "Test error location finding",
                "Test dependency analysis"
            ]
        }
        return suggestions.get(module_name, ["Add basic unit tests for public methods"])