#!/usr/bin/env python3
"""
Test runner for all MealMetrics tests
"""

import sys
import os
import subprocess
import importlib.util

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_test_file(test_file_path, test_name):
    """Run a specific test file"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_name}")
    print(f"{'='*60}")
    
    try:
        # Try to run as a module first
        if os.path.exists(test_file_path):
            result = subprocess.run([sys.executable, test_file_path], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"PASS: {test_name}")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                print(f"FAIL: {test_name}")
                if result.stderr:
                    print("STDERR:", result.stderr)
                if result.stdout:
                    print("STDOUT:", result.stdout)
                return False
        else:
            print(f"NOT FOUND: {test_name} - {test_file_path}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: {test_name} (60s)")
        return False
    except Exception as e:
        print(f"ERROR: {test_name} - {e}")
        return False

def run_all_tests():
    """Run all available tests"""
    print("MealMetrics Test Suite Runner")
    print("=" * 60)
    
    # Get the tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define test files and their descriptions
    test_files = [
        ("test_comprehensive.py", "Comprehensive Test Suite"),
        ("test_database.py", "Database Connection Tests"),
        ("test_improvements.py", "Bot Improvements Tests"),
        ("test_nb_note.py", "NB Note and Contextualization Tests"),
        ("test_mysql_connection.py", "MySQL Connection Tests"),
    ]
    
    results = []
    total_tests = len(test_files)
    
    print(f"Found {total_tests} test files to run...")
    
    for test_file, test_name in test_files:
        test_path = os.path.join(tests_dir, test_file)
        success = run_test_file(test_path, test_name)
        results.append((test_name, success))
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")

    passed = sum(1 for _, success in results if success)
    failed = total_tests - passed

    for test_name, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{test_name:<40} {status}")

    print(f"\nResults: {passed}/{total_tests} tests passed")

    if failed == 0:
        print("ALL TESTS PASSED! The MealMetrics bot is ready for deployment.")
        return True
    else:
        print(f"{failed} test(s) failed. Please check the output above for details.")
        return False

def run_specific_test(test_name):
    """Run a specific test by name"""
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Map test names to files
    test_map = {
        "comprehensive": "test_comprehensive.py",
        "database": "test_database.py",
        "improvements": "test_improvements.py",
        "nb": "test_nb_note.py",
        "mysql": "test_mysql_connection.py",
    }
    
    if test_name.lower() in test_map:
        test_file = test_map[test_name.lower()]
        test_path = os.path.join(tests_dir, test_file)
        return run_test_file(test_path, f"{test_name.title()} Tests")
    else:
        print(f"Unknown test: {test_name}")
        print(f"Available tests: {', '.join(test_map.keys())}")
        return False

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Run all tests
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
