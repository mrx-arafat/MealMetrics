#!/bin/bash

echo "========================================"
echo "MealMetrics Database User Checker"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed or not in PATH"
        echo "Please install Python and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check if we're in the database/check directory
if [ ! -f "quick_db_check.py" ]; then
    echo "Error: This doesn't look like the database/check directory"
    echo "Please run this from the MealMetrics/database/check folder"
    exit 1
fi

echo "Checking database..."
echo

# Run the quick check script
$PYTHON_CMD quick_db_check.py

echo
echo "========================================"
echo "Check complete!"
