#!/bin/bash

# Shell script to run all tests for microservices application

echo "Running tests for microservices application..."
echo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."

# Make the Python script executable
chmod +x "$SCRIPT_DIR/run_tests.py"

# Run the Python test script
python3 "$SCRIPT_DIR/run_tests.py" --project-root "$PROJECT_ROOT" "$@"
