#!/bin/bash

# AI Development Patterns Test Setup and Runner
# This script creates a Python 3.11 virtual environment, installs dependencies, and runs tests

set -e  # Exit on any error

echo "🚀 Setting up AI Development Patterns Test Environment"
echo "=================================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Virtual environment directory
VENV_DIR="$SCRIPT_DIR/venv"

# Step 1: Check if Python 3.11 is available
echo "📋 Checking Python 3.11 availability..."
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo "✅ Found python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    if [[ "$PYTHON_VERSION" == "3.11" ]]; then
        PYTHON_CMD="python3"
        echo "✅ Found python3 (version 3.11)"
    else
        echo "⚠️  Found python3 (version $PYTHON_VERSION), but prefer 3.11"
        PYTHON_CMD="python3"
    fi
else
    echo "❌ Python 3.11 not found. Please install Python 3.11"
    echo "   On macOS: brew install python@3.11"
    echo "   On Ubuntu: apt-get install python3.11 python3.11-venv"
    exit 1
fi

# Step 2: Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating Python virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo "✅ Virtual environment created at $VENV_DIR"
else
    echo "📦 Virtual environment already exists"
fi

# Step 3: Activate virtual environment
echo "🔄 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Verify we're in the virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Step 4: Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Step 5: Install test dependencies
echo "📥 Installing test dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed successfully"
else
    echo "❌ requirements.txt not found"
    deactivate
    exit 1
fi

# Step 6: Run the test program
echo ""
echo "🧪 Running AI Development Patterns Test Suite"
echo "=============================================="
echo ""

# Make sure run_all_tests.py is executable
chmod +x run_all_tests.py

# Run the tests
if ./run_all_tests.py; then
    TEST_EXIT_CODE=0
    echo ""
    echo "✅ Test suite completed successfully!"
else
    TEST_EXIT_CODE=$?
    echo ""
    echo "⚠️  Test suite completed with issues (exit code: $TEST_EXIT_CODE)"
fi

# Step 7: Show test results location
echo ""
echo "📊 Test Results:"
echo "   JSON Report: $SCRIPT_DIR/test-results/comprehensive_report.json"
echo "   Markdown Report: $SCRIPT_DIR/test-results/comprehensive_report.md"
echo ""

# Step 8: Deactivate virtual environment
echo "🔄 Deactivating virtual environment..."
deactivate
echo "✅ Virtual environment deactivated"

echo ""
echo "🎉 Setup and test run complete!"
echo "   Virtual environment: $VENV_DIR"
echo "   Test results: $SCRIPT_DIR/test-results/"

# Exit with the same code as the test suite
exit $TEST_EXIT_CODE