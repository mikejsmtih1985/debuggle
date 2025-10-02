#!/bin/bash
# Setup script for UI testing with Playwright

set -e

echo "🎭 Setting up Debuggle UI Test Suite"
echo "=================================="

# Install Python dependencies
echo "📦 Installing Python testing dependencies..."
pip install -r requirements-dev.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium firefox

# Create test directories
echo "📁 Creating test result directories..."
mkdir -p test-results
mkdir -p playwright-report

# Create pytest.ini configuration for UI tests
echo "⚙️ Creating pytest configuration..."
cat > pytest.ini << EOF
[tool:pytest]
minversion = 6.0
addopts = 
    -ra
    -q
    --strict-markers
    --strict-config
    --cov=src/debuggle
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --html=test-results/report.html
    --self-contained-html

testpaths = tests

markers =
    ui: UI tests that require a browser
    slow: Slow running tests
    websocket: Tests that require WebSocket functionality
    integration: Integration tests

# Playwright specific settings
playwright_browser = chromium
playwright_headed = false
playwright_slow_mo = 0

# Filter warnings
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
EOF

echo "✅ UI test setup complete!"
echo ""
echo "🚀 To run UI tests:"
echo "   # Run all UI tests:"
echo "   pytest tests/test_ui_*.py"
echo ""
echo "   # Run specific UI test categories:"
echo "   pytest -m ui                    # All UI tests"
echo "   pytest -m \"ui and not slow\"     # Fast UI tests only"
echo "   pytest tests/test_ui_tags.py    # Just tag interaction tests"
echo ""
echo "   # Run with browser visible (for debugging):"
echo "   pytest tests/test_ui_*.py --headed"
echo ""
echo "   # Generate HTML report:"
echo "   pytest tests/test_ui_*.py --html=test-results/ui-report.html"
echo ""
echo "⚠️  Make sure Debuggle server is running on localhost:8000 before running UI tests!"
echo "   Start server with: python entry_point.py serve"