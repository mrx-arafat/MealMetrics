#!/usr/bin/env python3
"""
Test NB note formatting with long descriptions
"""

import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.vision_analyzer import VisionAnalyzer

def test_long_description_formatting():
    """Test NB note with long food descriptions"""
    print("Testing NB Note with Long Descriptions:")
    print("=" * 50)
    
    analyzer = VisionAnalyzer()
    
    # Test with the exact description from your example
    long_description_analysis = {
        'description': 'A meal consisting of a curry dish with fried chicken and a side of fried rice, served in a metal tray with a compartment for onions.',
        'total_calories': 650,
        'confidence': 85,
        'health_category': 'moderate',
        'health_score': 6,
        'total_carbs': 75,
        'total_protein': 35,
        'total_fat': 25,
        'food_items': [
            {
                'name': 'Fried chicken curry',
                'portion': '200g',
                'calories': 400,
                'cooking_method': 'fried',
                'health_score': 5
            },
            {
                'name': 'Fried rice',
                'portion': '150g',
                'calories': 250,
                'cooking_method': 'fried',
                'health_score': 6
            }
        ],
        'witty_comment': 'A hearty meal with good protein content, though the frying adds extra calories.',
        'recommendations': 'Consider grilled chicken instead of fried for a healthier option.',
        'fun_fact': 'Rice is a staple food for over half the world\'s population.',
        'notes': 'Traditional curry meal with rice'
    }
    
    # Format the message
    formatted_message = analyzer.format_analysis_for_user(long_description_analysis)
    
    # Extract just the NB note line
    lines = formatted_message.split('\n')
    nb_line = None
    for line in lines:
        if 'NB:' in line:
            nb_line = line
            break
    
    print("Generated NB note:")
    print("-" * 50)
    print(nb_line)
    print("-" * 50)
    
    # Check that there are no backslashes
    if nb_line and '\\' not in nb_line:
        print("PASS: No backslashes found in NB note!")
    else:
        print("FAIL: Backslashes still present in NB note!")
        
    # Check that parentheses are present and not escaped
    if nb_line and '(' in nb_line and ')' in nb_line:
        print("PASS: Parentheses properly formatted!")
    else:
        print("FAIL: Parentheses missing or malformed!")
    
    # Check calorie range format
    expected_range = "600-700 kcal"
    if nb_line and expected_range in nb_line:
        print(f"PASS: Correct calorie range ({expected_range}) found!")
    else:
        print(f"FAIL: Expected calorie range ({expected_range}) not found!")
    
    print("\nFull message preview:")
    print("=" * 50)
    print(formatted_message[:500] + "..." if len(formatted_message) > 500 else formatted_message)
    print("=" * 50)

def main():
    """Run the test"""
    print("MealMetrics NB Note Formatting Test")
    print("=" * 50)
    
    try:
        test_long_description_formatting()
        print("\nNB note formatting test completed!")
        
    except Exception as e:
        print(f"\nTest failed: {e}")

if __name__ == "__main__":
    main()
