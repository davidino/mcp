#!/bin/bash
# Install dependencies and run tests for the CloudWatch MCP server
cd "$(dirname "$0")"

# Check if test virtual environment exists, create if not
if [ ! -d "test_venv" ]; then
    echo "Creating test virtual environment..."
    python3 -m venv test_venv
fi

# Activate virtual environment
source test_venv/bin/activate

# Install package in development mode with test dependencies
echo "Installing package and test dependencies..."
pip install -e ".[test]"

# Run tests
echo "Running tests..."
if [ "$1" == "--verbose" ] || [ "$1" == "-v" ]; then
    python -m pytest tests/unit/ -v
elif [ -n "$1" ]; then
    # If a specific test file or directory is provided
    python -m pytest "$1"
else
    # Run all tests
    python -m pytest tests/unit/
fi