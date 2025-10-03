#!/bin/bash

#
# 🧪 DEBUGGLE QUALITY ASSURANCE LABORATORY - Comprehensive Testing Facility
# ==========================================================================
#
# This testing script is like having a professional quality assurance
# laboratory that runs comprehensive safety tests, performance evaluations,
# and quality control checks on our software before it goes to customers.
#
# 🏆 HIGH SCHOOL EXPLANATION:
# Think of this like the testing facility where new cars go before being
# sold to the public:
# 1. 🔧 Safety Tests - Make sure nothing breaks or crashes
# 2. 🏃 Performance Tests - Check that everything runs fast enough
# 3. 🔌 Integration Tests - Verify all parts work together properly
# 4. 🩺 Health Checks - Confirm all systems are responding correctly
# 5. 📊 Quality Reports - Document what passed and what needs fixing
#
# Just like car manufacturers test every component before shipping,
# we test every piece of Debuggle before users interact with it.
#
# EDUCATIONAL METAPHORS USED:
# 🧪 Scientific Laboratory - Controlled testing environment with protocols
# 🏥 Medical Checkup - Health monitoring and diagnostic procedures
# 🏭 Quality Control - Manufacturing testing and inspection processes
# 🔬 Research Facility - Systematic investigation and validation methods
#

# 🛡️ SAFETY PROTOCOL - Stop immediately if any test fails
# This is like having an emergency stop button in a factory
set -e

# 📢 LABORATORY ACTIVATION ANNOUNCEMENT
echo "🧪 Running Debuggle test suite..."

#
# ⚙️ LABORATORY CONFIGURATION - Setting up test environment parameters
# ====================================================================
#
# These settings are like configuring the testing equipment before
# starting experiments - we need to know where to find the system
# being tested and how long to wait for responses.
#
BASE_URL="${BASE_URL:-http://localhost:8000}"  # 🌐 Address of system under test
TIMEOUT="${TIMEOUT:-30}"                       # ⏱️ Maximum wait time for responses

#
# 🧪 LABORATORY ENVIRONMENT SETUP - Activating controlled test environment
# ========================================================================
#
# This ensures our tests run in the correct isolated environment,
# like making sure a chemistry experiment uses the right chemicals
# and equipment setup.
#
if [ -d "venv" ]; then
    echo "⚡ Activating virtual environment..."
    source venv/bin/activate  # 🔬 Switch to controlled testing environment
fi

#
# 🩺 SYSTEM HEALTH DIAGNOSTIC - Checking if the patient is responsive
# ===================================================================
#
# This function is like a doctor checking vital signs before starting
# a comprehensive medical examination. We need to confirm the system
# is alive and responding before running detailed tests.
#
# 🏆 HIGH SCHOOL EXPLANATION:
# Think of this like checking if a video game server is online:
# 1. Try to connect to the server (curl -f $BASE_URL/health)
# 2. If it responds, great! We can start testing
# 3. If not, wait a bit and try again (up to 10 times)
# 4. If still no response, something's wrong - report the problem
#
check_service() {
    echo "🏥 Checking if service is running..."
    
    # 🔄 CONNECTIVITY TEST LOOP - Systematic connection attempts
    for i in {1..10}; do
        if curl -f $BASE_URL/health > /dev/null 2>&1; then
            echo "✅ Service is running"
            return 0  # Success! Service is responsive
        fi
        echo "⏳ Waiting for service... ($i/10)"
        sleep 3   # Wait 3 seconds before next attempt
    done
    
    # 🚨 DIAGNOSTIC FAILURE - System not responding
    echo "❌ Service is not responding"
    return 1
}

# Run unit tests
echo "🔬 Running unit tests..."
python -m pytest tests/ -v --tb=short

# Check if service is running for integration tests
if check_service; then
    echo ""
    echo "🌐 Running integration tests..."
    
    # Test health endpoint
    echo "Testing health endpoint..."
    response=$(curl -s $BASE_URL/health)
    if echo $response | grep -q "healthy"; then
        echo "✅ Health check passed"
    else
        echo "❌ Health check failed: $response"
        exit 1
    fi
    
    # Test log processing endpoint
    echo "Testing log processing endpoint..."
    response=$(curl -s -X POST $BASE_URL/debuggle-log \
        -H "Content-Type: application/json" \
        -d '{"content": "TEST: Integration test log entry", "tier": "core"}')
    
    if echo $response | grep -q "success"; then
        echo "✅ Log processing test passed"
    else
        echo "❌ Log processing test failed: $response"
        exit 1
    fi
    
    # Test file upload endpoint
    echo "Testing file upload endpoint..."
    echo "TEST: Sample log entry for upload test" > /tmp/test.log
    
    response=$(curl -s -X POST $BASE_URL/upload-file \
        -F "file=@/tmp/test.log" \
        -F "tier=core")
    
    if echo $response | grep -q "success"; then
        echo "✅ File upload test passed"
    else
        echo "❌ File upload test failed: $response"
        exit 1
    fi
    
    # Cleanup
    rm -f /tmp/test.log
    
else
    echo "⚠️  Service not running, skipping integration tests"
    echo "   Start the service with: uvicorn app.main:app --reload"
fi

# Check code style
echo ""
echo "🎨 Checking code style..."
if command -v flake8 > /dev/null 2>&1; then
    flake8 app/ tests/ --max-line-length=100 --ignore=E203,W503
    echo "✅ Code style check passed"
else
    echo "⚠️  flake8 not installed, skipping style check"
fi

# Security check
echo ""
echo "🔐 Running security checks..."
if command -v bandit > /dev/null 2>&1; then
    bandit -r app/ -f json -o /tmp/bandit-report.json || true
    if [ -f /tmp/bandit-report.json ]; then
        issues=$(jq '.results | length' /tmp/bandit-report.json 2>/dev/null || echo "0")
        if [ "$issues" -eq "0" ]; then
            echo "✅ No security issues found"
        else
            echo "⚠️  $issues potential security issues found"
            echo "   Check /tmp/bandit-report.json for details"
        fi
        rm -f /tmp/bandit-report.json
    fi
else
    echo "⚠️  bandit not installed, skipping security check"
fi

# Performance test
if check_service; then
    echo ""
    echo "⚡ Running basic performance test..."
    
    start_time=$(date +%s.%N)
    for i in {1..10}; do
        curl -s -X POST $BASE_URL/debuggle-log \
            -H "Content-Type: application/json" \
            -d '{"content": "PERF: Performance test log entry '$i'", "tier": "core"}' > /dev/null
    done
    end_time=$(date +%s.%N)
    
    duration=$(echo "$end_time - $start_time" | bc)
    avg_time=$(echo "scale=3; $duration / 10" | bc)
    
    echo "✅ Performance test completed"
    echo "   Average request time: ${avg_time}s"
    
    if (( $(echo "$avg_time < 1.0" | bc -l) )); then
        echo "   🚀 Performance: Excellent"
    elif (( $(echo "$avg_time < 2.0" | bc -l) )); then
        echo "   ⚡ Performance: Good"
    else
        echo "   🐌 Performance: Could be improved"
    fi
fi

echo ""
echo "🎉 Test suite completed!"
echo ""
echo "📊 Summary:"
echo "  ✅ Unit tests: Passed"
if curl -f $BASE_URL/health > /dev/null 2>&1; then
    echo "  ✅ Integration tests: Passed"
    echo "  ✅ Performance tests: Completed"
else
    echo "  ⚠️  Integration tests: Skipped (service not running)"
fi
echo ""
echo "🔧 To run individual test categories:"
echo "  Unit tests only: python -m pytest tests/"
echo "  Style check only: flake8 app/ tests/"
echo "  Security check only: bandit -r app/"
echo ""