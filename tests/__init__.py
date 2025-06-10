"""
MealMetrics Test Suite

This package contains all test modules for the MealMetrics bot.

Test Structure:
- test_comprehensive.py: Comprehensive test suite for all components
- test_database.py: Database-specific tests
- test_improvements.py: Tests for recent improvements
- test_mysql_connection.py: MySQL connection tests
- test_helpers.py: Helper function tests
- test_config.py: Configuration tests
- test_vision_analyzer.py: AI vision analyzer tests
- test_bot_handlers.py: Bot handler tests

Usage:
    # Run all tests
    python -m pytest tests/
    
    # Run specific test file
    python tests/test_comprehensive.py
    
    # Run with verbose output
    python -m pytest tests/ -v
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
