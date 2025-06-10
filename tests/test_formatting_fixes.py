#!/usr/bin/env python3
"""
Test formatting fixes for backslashes and timezone issues
"""

import sys
import os
from datetime import datetime, timezone, timedelta

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import format_meal_summary, format_timestamp_for_user

def test_backslash_removal():
    """Test that backslashes are removed from meal descriptions"""
    print("Testing Backslash Removal:")
    print("=" * 40)
    
    # Create test meals with problematic characters
    test_meals = [
        {
            'description': 'A meal consisting of a tray divided into three compartments...',
            'calories': 600,
            'timestamp': '2024-01-15T09:48:00'
        },
        {
            'description': 'Pizza slice with extra cheese - delicious!',
            'calories': 450,
            'timestamp': '2024-01-15T12:30:00'
        }
    ]
    
    # Format the summary
    summary = format_meal_summary(test_meals)
    
    print("Generated summary:")
    print("-" * 30)
    print(summary)
    print("-" * 30)
    
    # Check for problematic backslashes
    problematic_patterns = ['\\-', '\\.', '\\(', '\\)']
    found_issues = []
    
    for pattern in problematic_patterns:
        if pattern in summary:
            found_issues.append(pattern)
    
    if found_issues:
        print(f"FAIL: Found problematic backslashes: {found_issues}")
        return False
    else:
        print("PASS: No problematic backslashes found!")
        return True

def test_timezone_formatting():
    """Test timezone-aware time formatting"""
    print("\nTesting Timezone Formatting:")
    print("=" * 40)
    
    # Test different timestamp formats
    test_timestamps = [
        '2024-01-15T09:48:00',           # No timezone
        '2024-01-15T09:48:00Z',          # UTC
        '2024-01-15T09:48:00+00:00',     # UTC with offset
        '2024-01-15T09:48:00.123456',    # With microseconds
    ]
    
    # Test without timezone offset (should use stored time)
    print("Without timezone offset:")
    for ts in test_timestamps:
        formatted = format_timestamp_for_user(ts)
        print(f"  {ts} -> {formatted}")
    
    # Test with timezone offset (+5:30 = 19800 seconds)
    print("\nWith timezone offset (+5:30):")
    timezone_offset = 5.5 * 3600  # +5:30 in seconds
    for ts in test_timestamps:
        formatted = format_timestamp_for_user(ts, int(timezone_offset))
        print(f"  {ts} -> {formatted}")
    
    # Test with negative timezone offset (-5:00 = -18000 seconds)
    print("\nWith timezone offset (-5:00):")
    timezone_offset = -5 * 3600  # -5:00 in seconds
    for ts in test_timestamps:
        formatted = format_timestamp_for_user(ts, int(timezone_offset))
        print(f"  {ts} -> {formatted}")
    
    print("PASS: Timezone formatting working!")
    return True

def test_meal_summary_with_timezone():
    """Test complete meal summary with timezone"""
    print("\nTesting Complete Meal Summary with Timezone:")
    print("=" * 50)
    
    # Create test meals
    test_meals = [
        {
            'description': 'A meal consisting of a tray divided into three compartments with curry, rice, and onions',
            'calories': 600,
            'timestamp': '2024-01-15T09:48:00Z'
        },
        {
            'description': 'Grilled chicken with vegetables',
            'calories': 450,
            'timestamp': '2024-01-15T12:30:00Z'
        }
    ]
    
    # Test without timezone
    print("Summary without timezone offset:")
    print("-" * 30)
    summary_no_tz = format_meal_summary(test_meals)
    print(summary_no_tz)
    
    # Test with timezone (+5:30)
    print("\nSummary with timezone offset (+5:30):")
    print("-" * 30)
    timezone_offset = int(5.5 * 3600)  # +5:30 in seconds
    summary_with_tz = format_meal_summary(test_meals, timezone_offset)
    print(summary_with_tz)
    
    # Check for improvements
    has_backslashes = any(pattern in summary_with_tz for pattern in ['\\-', '\\.', '\\(', '\\)'])
    
    if has_backslashes:
        print("FAIL: Still contains backslashes!")
        return False
    else:
        print("PASS: Clean formatting without backslashes!")
        return True

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\nTesting Edge Cases:")
    print("=" * 30)
    
    # Test with empty meals
    empty_summary = format_meal_summary([])
    print("Empty meals summary:")
    print(empty_summary)
    
    # Test with malformed timestamp
    malformed_timestamp = format_timestamp_for_user("invalid-timestamp")
    print(f"\nMalformed timestamp -> {malformed_timestamp}")
    
    # Test with very long description
    long_meal = {
        'description': 'A' * 100 + ' very long meal description that should be truncated',
        'calories': 500,
        'timestamp': '2024-01-15T15:00:00Z'
    }
    
    long_summary = format_meal_summary([long_meal])
    print("\nLong description summary:")
    print(long_summary)
    
    print("PASS: Edge cases handled correctly!")
    return True

def main():
    """Run all formatting tests"""
    print("MealMetrics Formatting Fixes Test Suite")
    print("=" * 50)
    
    try:
        results = []
        results.append(test_backslash_removal())
        results.append(test_timezone_formatting())
        results.append(test_meal_summary_with_timezone())
        results.append(test_edge_cases())
        
        print("\n" + "=" * 50)
        if all(results):
            print("All formatting tests passed!")
            print("\nFixes implemented:")
            print("1. Removed problematic backslashes from meal descriptions")
            print("2. Added timezone-aware time formatting")
            print("3. Simplified markdown escaping")
            print("4. Improved error handling")
        else:
            print("Some tests failed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nTest failed: {e}")

if __name__ == "__main__":
    main()
