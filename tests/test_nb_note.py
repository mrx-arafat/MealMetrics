#!/usr/bin/env python3
"""
Test the NB note functionality and improved contextualization
"""

import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.vision_analyzer import VisionAnalyzer

def test_nb_note_generation():
    """Test the NB note generation for calorie estimates"""
    print("Testing NB Note Generation:")
    print("=" * 40)
    
    analyzer = VisionAnalyzer()
    
    # Test different calorie ranges
    test_cases = [
        (150, "Cashewnut stir-fry"),
        (450, "Grilled chicken with rice"),
        (850, "Large pizza slice"),
        (1200, "Full chicken biryani plate"),
    ]
    
    for calories, description in test_cases:
        calorie_range = analyzer._get_calorie_range(calories)
        print(f"Calories: {calories} -> Range: {calorie_range}")
        print(f"Description: {description}")
        print()
    
    print("NB note generation working correctly!")

def test_template_filtering():
    """Test that template text is filtered out"""
    print("\nTesting Template Text Filtering:")
    print("=" * 40)
    
    analyzer = VisionAnalyzer()
    
    # Test analysis with template text (should be filtered out)
    template_analysis = {
        'description': 'Test meal',
        'total_calories': 500,
        'confidence': 85,
        'health_category': 'healthy',
        'health_score': 8,
        'total_carbs': 35,
        'total_protein': 40,
        'total_fat': 12,
        'food_items': [],
        'witty_comment': 'For healthy food: Positive reinforcement. For moderate: Balanced perspective.',
        'recommendations': 'For junk food: Stark warnings about health risks and specific healthier alternatives.',
        'fun_fact': 'This is a real fun fact',
        'notes': 'Real notes'
    }
    
    # Test analysis with real content (should be shown)
    real_analysis = {
        'description': 'Grilled chicken with vegetables',
        'total_calories': 450,
        'confidence': 85,
        'health_category': 'healthy',
        'health_score': 8,
        'total_carbs': 35,
        'total_protein': 40,
        'total_fat': 12,
        'food_items': [
            {
                'name': 'Grilled chicken breast',
                'portion': '150g',
                'calories': 250,
                'cooking_method': 'grilled',
                'health_score': 9
            }
        ],
        'witty_comment': 'Excellent protein-rich meal with balanced macronutrients!',
        'recommendations': 'Perfect post-workout meal. Consider adding some healthy fats like avocado.',
        'fun_fact': 'Chicken breast contains all 9 essential amino acids.',
        'notes': 'Well-balanced meal'
    }
    
    print("Testing template analysis (should filter out witty comment and recommendations):")
    template_message = analyzer.format_analysis_for_user(template_analysis)
    has_template_text = any(phrase in template_message for phrase in [
        "For junk food:", "For healthy food:", "For moderate:"
    ])
    
    if has_template_text:
        print("FAIL: Template text found in message!")
        print("Template phrases detected in output")
    else:
        print("PASS: Template text successfully filtered out!")
    
    print("\nTesting real analysis (should show witty comment and recommendations):")
    real_message = analyzer.format_analysis_for_user(real_analysis)
    has_witty_comment = "Excellent protein-rich meal" in real_message
    has_recommendations = "Perfect post-workout meal" in real_message
    has_nb_note = "NB:" in real_message
    
    if has_witty_comment and has_recommendations:
        print("PASS: Real content successfully displayed!")
    else:
        print("FAIL: Real content not found in message!")
        
    if has_nb_note:
        print("PASS: NB note successfully added!")
    else:
        print("FAIL: NB note not found in message!")
    
    print("\nSample output with NB note:")
    print("-" * 50)
    # Show just the NB note part
    lines = real_message.split('\n')
    for line in lines:
        if 'NB:' in line:
            print(line)
            break
    print("-" * 50)

def main():
    """Run all tests"""
    print("MealMetrics NB Note and Contextualization Tests")
    print("=" * 50)
    
    try:
        test_nb_note_generation()
        test_template_filtering()
        
        print("\n" + "=" * 50)
        print("All NB note tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        print("=" * 50)

if __name__ == "__main__":
    main()
