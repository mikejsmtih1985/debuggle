#
# 📚 DEBUGGLE RECIPE BOOK - Professional Kitchen Automation System
# =================================================================
#
# This Makefile is like a comprehensive cookbook for professional chefs that
# contains all the standard recipes, procedures, and shortcuts needed to
# operate a high-end restaurant kitchen efficiently.
#
# 🏆 HIGH SCHOOL EXPLANATION:
# Think of this like the master recipe collection at a restaurant chain:
# - Each recipe (target) has a clear name like "dev" or "test"
# - Follow the steps exactly and you get consistent results
# - Instead of remembering complex procedures, just say "make dev"
# - New kitchen staff can quickly learn all the standard procedures
# - Prevents mistakes by standardizing common tasks
#
# Instead of typing long, complex commands, you can use simple shortcuts:
# "make dev" instead of "uvicorn src.debuggle.main:app --reload --host 0.0.0.0 --port 8000"
#
# EDUCATIONAL METAPHORS USED:
# 📚 Recipe Book - Standard procedures and cooking instructions
# 👨‍🍳 Professional Kitchen - Organized, efficient workflow systems
# 🔧 Workshop Tools - Automated tools that make complex tasks simple
# 🏭 Assembly Line - Standardized processes for consistent results
#

#
# 🚀 DEVELOPMENT SERVER RECIPE - Start your coding workspace
# =========================================================
#
# This is like the "daily setup" procedure that gets your kitchen ready
# for a day of cooking. It starts the web server in development mode
# with all the features developers need.
#
# 🏆 HIGH SCHOOL EXPLANATION:
# Think of this like starting up a food truck:
# 1. Turn on all the equipment (uvicorn server)
# 2. Set it to "learning mode" (--reload) so it adapts to menu changes
# 3. Open for business from any location (--host 0.0.0.0)
# 4. Set up at the usual spot (--port 8000)
#
dev:
	uvicorn src.debuggle.main:app --reload --host 0.0.0.0 --port 8000

#
# 📦 BASIC INGREDIENT PROCUREMENT - Install essential supplies
# ===========================================================
#
# This recipe gets all the basic ingredients (Python packages) your
# project needs to function, like stocking a kitchen with flour,
# sugar, and other essentials.
#
install:
	pip install -r requirements.txt

#
# 🧪 ADVANCED CHEF TOOLKIT - Install development and testing tools
# ================================================================
#
# This recipe includes everything from the basic kit plus specialized
# tools that professional developers use, like having both basic knives
# and advanced molecular gastronomy equipment.
#
install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

#
# 🔗 LIVE KITCHEN CONNECTION - Install in "chef's choice" mode
# ===========================================================
#
# This installs your project in "editable" mode, meaning changes to
# your code are immediately available. Like having your recipe book
# connected directly to the kitchen - any updates appear instantly.
#
install-local:
	pip install -e .

#
# ✅ QUALITY CONTROL TEST - Basic food safety inspection
# ======================================================
#
# This runs all your automated tests to make sure everything works
# correctly, like having a food safety inspector check that all
# your dishes meet health standards.
#
test:
	pytest tests/ -v

#
# 📊 COMPREHENSIVE QUALITY AUDIT - Detailed safety inspection with reporting
# ==========================================================================
#
# This runs tests AND generates detailed reports showing exactly which
# parts of your code were tested, like having a full restaurant
# inspection with a detailed written report.
#
test-cov:
	pytest --cov=src/debuggle --cov-report=html --cov-report=term-missing

# Run UI tests
test-ui:
	./run_ui_tests.py

# Run UI tests with visible browser (for debugging)
test-ui-debug:
	./run_ui_tests.py --headed --debug

# Run specific UI test categories
test-ui-basic:
	./run_ui_tests.py --category basic

test-ui-tags:
	./run_ui_tests.py --category tags

test-ui-upload:
	./run_ui_tests.py --category upload

test-ui-websocket:
	./run_ui_tests.py --category websocket

test-ui-integration:
	./run_ui_tests.py --category integration

# Setup UI testing environment
setup-ui-tests:
	./setup_ui_tests.sh

# Run all tests (unit + UI)
test-all:
	pytest tests/ -v --ignore=tests/test_ui_*.py
	./run_ui_tests.py

# Generate comprehensive test report with UI tests
test-report:
	./run_ui_tests.py --report

#
# 🎨 PRESENTATION PREPARATION - Making dishes look professional
# ===========================================================
#
# This formats all your Python code to look neat and consistent,
# like having a sous chef arrange all the plates the same way
# before sending them to the dining room.
#
format:
	black src/ tests/ cli/ examples/
	
#
# 🔍 QUALITY INSPECTION - Head chef checking for mistakes
# ======================================================
#
# This runs quality checks on your code to catch common problems,
# like having an experienced chef taste-test everything and
# check for proper seasoning before it goes to customers.
#
lint:
	flake8 src/ tests/ cli/ examples/
	mypy src/

#
# 📝 INGREDIENT VERIFICATION - Checking recipe specifications
# =========================================================
#
# This specifically checks that all your data types are correct,
# like verifying that when a recipe calls for "2 cups flour"
# you're actually using flour and not sugar.
#
typecheck:
	mypy src/debuggle

#
# 🔧 COMMAND LINE TOOL - The kitchen's Swiss Army knife
# ====================================================
#
# This starts up the command-line version of Debuggle,
# like pulling out your best knife when you need to
# do precision work in the kitchen.
#
cli:
	python cli/debuggle_cli.py

#
# 📚 DEMONSTRATION RECIPES - Showing off signature dishes  
# =======================================================
#
# This runs example programs to demonstrate what Debuggle can do,
# like a cooking demonstration where you show customers
# your best recipes and techniques.
#
examples:
	cd examples && python demo_errors.py

#
# 📦 PACKAGE PREPARATION - Boxing up the final product
# ===================================================
#
# This builds a distributable package of your application,
# like packaging your homemade sauce in professional jars
# ready to sell in stores.
#
build:
	python -m build

#
# 🏭 INDUSTRIAL KITCHEN SETUP - Building the commercial kitchen
# ============================================================
#
# This creates a Docker container image with your application,
# like building a complete commercial kitchen that can be shipped
# anywhere and set up quickly with all the right equipment.
#
docker-build:
	cd docker && docker build -t debuggle-core:latest -f Dockerfile ..

#
# 🚀 RESTAURANT OPENING - Starting the full service operation
# ==========================================================
#
# This starts up the complete application with all services,
# like opening your restaurant for business with the kitchen,
# dining room, and wait staff all ready to serve customers.
#
docker-up:
	cd docker && docker-compose up --build

#
# 🔒 CLOSING TIME - Shutting down the restaurant for the night
# ===========================================================
#
# This gracefully stops all the Docker services,
# like closing your restaurant: turning off the ovens,
# cleaning up, and locking the doors.
#
docker-down:
	cd docker && docker-compose down

#
# 🧹 DEEP CLEANING - Full kitchen sanitization and reset
# =====================================================
#
# This stops everything and cleans up all temporary files,
# like doing a deep clean of the entire restaurant:
# washing all dishes, wiping all surfaces, and removing leftovers.
#
docker-clean:
	cd docker && docker-compose down -v
	docker image prune -f

#
# 🗑️ KITCHEN CLEANUP - Removing all the cooking scraps
# ====================================================
#
# This removes all temporary files created during development,
# like cleaning up flour spills, washing dirty bowls, and
# throwing away vegetable peels after a big cooking session.
#
clean:
	rm -rf build/          # Remove build artifacts (like dirty mixing bowls)
	rm -rf dist/           # Remove distribution packages (like packaged leftovers)
	rm -rf *.egg-info/     # Remove package info (like recipe notes)
	rm -rf .pytest_cache/  # Remove test cache (like cleaning the taste-testing spoons)
	rm -rf htmlcov/        # Remove coverage reports (like cleaning up test kitchen reports)
	find . -type d -name __pycache__ -delete    # Remove Python cache files
	find . -type f -name "*.pyc" -delete        # Remove compiled Python files

#
# 🏗️ KITCHEN RENOVATION - Setting up a brand new cooking space
# ===========================================================
#
# This sets up a complete development environment from scratch,
# like renovating a kitchen with new appliances, installing
# all the right tools, and stocking it with ingredients.
#
setup:
	python -m venv .venv                                          # Create virtual environment (like building a private prep kitchen)
	.venv/bin/pip install -r requirements.txt -r requirements-dev.txt  # Install all dependencies (like stocking ingredients and tools)
	.venv/bin/pip install -e .                                   # Install the project in development mode
	.venv/bin/pre-commit install                                 # Set up code quality hooks (like installing quality control systems)

#
# 🔍 KITCHEN INSPECTION - Making sure everything works perfectly
# =============================================================
#
# This runs a series of basic checks to make sure your kitchen
# is set up correctly, like testing that the ovens heat up,
# the refrigerator is cold, and all your tools are in place.
#
check:
	python -c "import src.debuggle; print('✅ Import successful')"  # Test that the main recipe book is readable
	python cli/debuggle_cli.py --help                               # Test that the command-line tools work
	pytest --collect-only                                           # Test that all recipe tests are findable

#
# 📋 RECIPE BOOK INDEX - List of all available cooking procedures
# ==============================================================
#
# This magical line tells Make that all these recipe names are "phony" -
# meaning they're commands to run, not files to create. Like having
# a table of contents that says "these are cooking instructions, not ingredients."
#
.PHONY: dev install install-dev install-local test test-cov format lint typecheck cli examples build docker-build docker-up docker-down docker-clean clean setup check

#
# 📖 RECIPE MENU - Your complete cookbook table of contents
# ========================================================
#
# This displays a helpful menu of all available recipes,
# like having a laminated reference card posted in your kitchen
# that shows all the dishes you can make and how to make them.
#
help:
	@echo "🍳 DEBUGGLE KITCHEN - Available Recipes:"
	@echo "================================================"
	@echo "🔥 Development & Testing:"
	@echo "  dev      - Start development server (fire up the stove)"
	@echo "  install  - Install Python dependencies (stock the pantry)"
	@echo "  test     - Run unit test suite (taste-test individual dishes)"
	@echo "  test-cov - Run tests with coverage report (comprehensive quality review)"
	@echo "  test-ui  - Run UI tests (test the dining experience)"
	@echo "  test-all - Run all tests (full restaurant inspection)"
	@echo ""
	@echo "🎨 Code Quality & Presentation:"
	@echo "  format   - Format code with black (arrange plates professionally)"
	@echo "  lint     - Lint code with flake8 (head chef quality check)"
	@echo "  typecheck- Type checking with mypy (verify recipe ingredients)"
	@echo ""
	@echo "🏭 Production & Deployment:"
	@echo "  build    - Build Docker image (construct commercial kitchen)"
	@echo "  docker-up- Start with Docker Compose (open restaurant for business)"
	@echo "  docker-down - Stop Docker Compose (close restaurant for night)"
	@echo "  clean    - Clean up build artifacts (kitchen cleanup)"
	@echo ""
	@echo "🔧 Utilities:"
	@echo "  cli      - Run command-line tool (use kitchen Swiss Army knife)"
	@echo "  examples - Run demonstration recipes (cooking show)"
	@echo "  setup    - Setup development environment (renovate kitchen)"
	@echo "  check    - Verify project structure (kitchen inspection)"
	@echo "  help     - Show this help message (display cookbook index)"

# This final line ensures all commands are treated as actions, not files
.PHONY: dev install test test-cov format lint build up down clean deploy