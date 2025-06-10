# MealMetrics Test Suite

This directory contains all test files for the MealMetrics bot project.

## 📁 Test Files

### Core Test Files

- **`test_comprehensive.py`** - Comprehensive test suite covering all major components
  - Helper function tests
  - Configuration validation tests
  - Database operation tests
  - Vision analyzer tests

- **`test_database.py`** - Database connection and operation tests
  - SQLite and MySQL connection testing
  - Table creation and initialization
  - User operations testing
  - Meal operations testing

- **`test_improvements.py`** - Tests for recent bot improvements
  - Dynamic food examples system
  - Emoji encoding tests
  - Message formatting tests
  - Reality check system for junk food

- **`test_mysql_connection.py`** - Specific MySQL connection tests
  - Network connectivity testing
  - MySQL server connection
  - Database creation and selection
  - Permission testing

### Utility Files

- **`run_all_tests.py`** - Test runner for executing all tests
- **`__init__.py`** - Package initialization with path setup

## 🚀 Running Tests

### Run All Tests
```bash
# From the MealMetrics directory
python tests/run_all_tests.py

# Or from the tests directory
python run_all_tests.py
```

### Run Specific Tests
```bash
# Run comprehensive tests
python tests/run_all_tests.py comprehensive

# Run database tests
python tests/run_all_tests.py database

# Run improvements tests
python tests/run_all_tests.py improvements

# Run MySQL tests
python tests/run_all_tests.py mysql
```

### Run Individual Test Files
```bash
# Run comprehensive tests directly
python tests/test_comprehensive.py

# Run database tests directly
python tests/test_database.py

# Run improvements tests directly
python tests/test_improvements.py

# Run MySQL tests directly
python tests/test_mysql_connection.py
```

## 📊 Test Coverage

### Helper Functions
- ✅ Calorie formatting
- ✅ Numeric value parsing
- ✅ Markdown escaping
- ✅ Input sanitization
- ✅ User input validation
- ✅ Confidence formatting
- ✅ Image format validation

### Configuration
- ✅ Valid configuration validation
- ✅ Missing token detection
- ✅ Invalid token format detection
- ✅ Database configuration validation

### Database Operations
- ✅ Meal logging
- ✅ User statistics
- ✅ Daily summaries
- ✅ Pending meals
- ✅ Data clearing operations

### Vision Analyzer
- ✅ Analysis formatting
- ✅ Healthy food formatting
- ✅ Junk food reality check formatting
- ✅ Markdown escaping in messages

### Bot Improvements
- ✅ Dynamic food examples
- ✅ Emoji encoding
- ✅ Enhanced message formatting
- ✅ Reality check system

## 🔧 Test Requirements

### Dependencies
All test dependencies are included in the main `requirements.txt`:
- `python-telegram-bot`
- `pillow`
- `mysql-connector-python` (for MySQL tests)

### Environment Setup
For database tests, ensure you have:
- Valid `.env` file with configuration
- Database credentials (if testing MySQL)
- Proper permissions for file creation (SQLite tests)

## 📈 Test Results

Expected output for successful test run:
```
🚀 MealMetrics Test Suite Runner
============================================================
Found 4 test files to run...

============================================================
🧪 Running Comprehensive Test Suite
============================================================
✅ Comprehensive Test Suite - PASSED

============================================================
🧪 Running Database Connection Tests
============================================================
✅ Database Connection Tests - PASSED

============================================================
🧪 Running Bot Improvements Tests
============================================================
✅ Bot Improvements Tests - PASSED

============================================================
🧪 Running MySQL Connection Tests
============================================================
✅ MySQL Connection Tests - PASSED

============================================================
📊 TEST SUMMARY
============================================================
Comprehensive Test Suite                ✅ PASSED
Database Connection Tests               ✅ PASSED
Bot Improvements Tests                  ✅ PASSED
MySQL Connection Tests                  ✅ PASSED

📈 Results: 4/4 tests passed
🎉 ALL TESTS PASSED! The MealMetrics bot is ready for deployment.
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running tests from the correct directory
   - Check that all dependencies are installed

2. **Database Connection Failures**
   - Verify `.env` file configuration
   - Check database server status
   - Ensure proper permissions

3. **Test Timeouts**
   - Check network connectivity
   - Verify API keys are valid
   - Ensure database server is responsive

### Debug Mode
For detailed error information, run tests individually:
```bash
python tests/test_comprehensive.py
```

## 📝 Adding New Tests

To add new tests:

1. Create a new test file in the `tests/` directory
2. Follow the naming convention: `test_<feature>.py`
3. Add the test to `run_all_tests.py` in the `test_files` list
4. Update this README with the new test description

### Test Template
```python
#!/usr/bin/env python3
"""
Test description
"""

import sys
import os
import unittest

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Your imports here

class TestYourFeature(unittest.TestCase):
    """Test your feature"""
    
    def test_something(self):
        """Test something specific"""
        # Your test code here
        pass

if __name__ == "__main__":
    unittest.main()
```
