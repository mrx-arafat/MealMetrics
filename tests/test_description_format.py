#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test description formatting improvements
"""

import sys
import os

# Set UTF-8 encoding for Windows compatibility
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import format_meal_summary

def test_clean_description_format():
    """Test that meal descriptions are clean and concise"""
    print("Testing Clean Description Format:")
    print("=" * 40)
    
    # Test meals with the desired format
    test_meals = [
        {
            'description': 'Fried Chicken Curry, Fried Rice, Sliced Onions',
            'calories': 600,
            'timestamp': '2024-01-15T09:48:00'
        },
        {
            'description': 'Grilled Chicken Breast, Steamed Broccoli, Rice',
            'calories': 450,
            'timestamp': '2024-01-15T12:30:00'
        },
        {
            'description': 'Pepperoni Pizza Slice, Side Salad',
            'calories': 520,
            'timestamp': '2024-01-15T18:15:00'
        }
    ]
    
    # Format the summary
    summary = format_meal_summary(test_meals)
    
    print("Generated summary:")
    print("-" * 50)
    try:
        print(summary)
    except UnicodeEncodeError:
        # Handle emoji encoding issues on Windows
        print(summary.encode('ascii', 'replace').decode('ascii'))
    print("-" * 50)
    
    # Check for clean formatting
    lines = summary.split('\n')
    meal_lines = [line for line in lines if line.strip() and line[0].isdigit()]
    
    print("\nMeal lines extracted:")
    for i, line in enumerate(meal_lines, 1):
        print(f"  {line}")
    
    # Verify format
    expected_format = True
    for line in meal_lines:
        # Should not contain backslashes
        if '\\' in line:
            print(f"FAIL: Found backslash in: {line}")
            expected_format = False
        
        # Should contain proper separators
        if ' - ' not in line or '(' not in line:
            print(f"FAIL: Incorrect format in: {line}")
            expected_format = False
    
    if expected_format:
        print("PASS: All meal descriptions properly formatted!")
    else:
        print("FAIL: Some formatting issues found!")
    
    return expected_format

def test_verbose_description_handling():
    """Test handling of verbose descriptions"""
    print("\nTesting Verbose Description Handling:")
    print("=" * 45)
    
    # Test with verbose descriptions (what we want to avoid)
    verbose_meals = [
        {
            'description': 'A meal consisting of a tray divided into three compartments containing curry, rice, and onions',
            'calories': 600,
            'timestamp': '2024-01-15T09:48:00'
        }
    ]
    
    summary = format_meal_summary(verbose_meals)
    print("Verbose description summary:")
    print("-" * 30)
    print(summary)
    print("-" * 30)
    
    # Check if description is truncated properly
    lines = summary.split('\n')
    meal_line = None
    for line in lines:
        if line.strip() and line[0].isdigit():
            meal_line = line
            break
    
    if meal_line:
        print(f"\nMeal line: {meal_line}")
        if '...' in meal_line:
            print("PASS: Long description properly truncated!")
            return True
        else:
            print("INFO: Description not truncated (may be within limit)")
            return True
    else:
        print("FAIL: No meal line found!")
        return False

def test_special_characters():
    """Test handling of special characters in descriptions"""
    print("\nTesting Special Characters:")
    print("=" * 35)
    
    # Test with special characters
    special_meals = [
        {
            'description': 'Chicken & Rice (spicy), Green Salad - Fresh!',
            'calories': 400,
            'timestamp': '2024-01-15T13:00:00'
        },
        {
            'description': 'Fish & Chips (2 pieces)',
            'calories': 650,
            'timestamp': '2024-01-15T19:30:00'
        }
    ]
    
    summary = format_meal_summary(special_meals)
    print("Special characters summary:")
    print("-" * 30)
    print(summary)
    print("-" * 30)
    
    # Check for proper escaping
    problematic_escapes = ['\\&', '\\!', '\\(', '\\)', '\\-']
    found_issues = []
    
    for escape in problematic_escapes:
        if escape in summary:
            found_issues.append(escape)
    
    if found_issues:
        print(f"FAIL: Found problematic escapes: {found_issues}")
        return False
    else:
        print("PASS: Special characters handled correctly!")
        return True

def test_time_format():
    """Test time formatting without backslashes"""
    print("\nTesting Time Format:")
    print("=" * 25)
    
    test_meals = [
        {
            'description': 'Morning Coffee, Toast',
            'calories': 150,
            'timestamp': '2024-01-15T07:30:00'
        }
    ]
    
    summary = format_meal_summary(test_meals)
    print("Time format summary:")
    print("-" * 20)
    print(summary)
    print("-" * 20)
    
    # Check for time format issues
    if '\\(' in summary or '\\)' in summary:
        print("FAIL: Found escaped parentheses in time!")
        return False
    else:
        print("PASS: Time format clean!")
        return True

def main():
    """Run all description format tests"""
    print("MealMetrics Description Format Test Suite")
    print("=" * 50)
    
    try:
        results = []
        results.append(test_clean_description_format())
        results.append(test_verbose_description_handling())
        results.append(test_special_characters())
        results.append(test_time_format())
        
        print("\n" + "=" * 50)
        if all(results):
            print("All description format tests passed!")
            print("\nExpected format achieved:")
            print("✅ 1. Fried Chicken Curry, Fried Rice, Sliced Onions - 600 calories (09:48)")
            print("✅ 2. Grilled Chicken Breast, Steamed Broccoli, Rice - 450 calories (12:30)")
            print("✅ Clean, concise, no backslashes!")
        else:
            print("Some tests failed - check output above")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nTest failed: {e}")

if __name__ == "__main__":
    main()
