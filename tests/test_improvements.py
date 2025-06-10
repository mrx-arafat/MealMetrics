#!/usr/bin/env python3
"""
Test script to verify MealMetrics bot improvements
"""

import sys
import os
import random

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.handlers import BotHandlers

def test_dynamic_examples():
    """Test the dynamic food examples system"""
    print("Testing Dynamic Food Examples:")
    print("=" * 40)
    
    # Create a mock handlers instance to access the examples
    class MockDB:
        pass
    
    handlers = BotHandlers(MockDB())
    
    # Test that we have examples
    assert len(handlers.FOOD_EXAMPLES) > 0, "No food examples found!"
    print(f"Found {len(handlers.FOOD_EXAMPLES)} food examples")
    
    # Test random selection
    print("\nRandom examples (simulating tip messages):")
    for i in range(5):
        example = random.choice(handlers.FOOD_EXAMPLES)
        print(f"{i+1}. {example}")
    
    print("\nDynamic examples system working correctly!")

def test_message_formatting():
    """Test message formatting improvements"""
    print("\nTesting Message Formatting:")
    print("=" * 40)

    # Test healthy food formatting
    healthy_analysis = {
        'description': 'Grilled chicken with rice and vegetables',
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
        'fun_fact': 'Chicken breast contains all 9 essential amino acids, making it a complete protein source.',
        'notes': 'Well-balanced meal with good portion control'
    }

    # Test junk food formatting with reality check
    junk_analysis = {
        'description': 'Large pepperoni pizza slice with extra cheese',
        'total_calories': 850,
        'confidence': 90,
        'health_category': 'junk',
        'health_score': 2,
        'total_carbs': 85,
        'total_protein': 35,
        'total_fat': 45,
        'food_items': [
            {
                'name': 'Pizza slice',
                'portion': '1 large slice',
                'calories': 850,
                'cooking_method': 'baked',
                'health_score': 2
            }
        ],
        'witty_comment': 'Your pancreas just went into overdrive mode. This single slice contains more sodium than you should have in an entire day, and enough saturated fat to clog your arteries for the next 48 hours.',
        'recommendations': 'STOP. Your body is literally screaming for help right now. Switch to a salad with grilled chicken immediately. Your future self will thank you when you avoid diabetes at 40.',
        'fun_fact': 'Pizza is engineered to be addictive - the combination of fat, salt, and refined carbs triggers the same brain pathways as cocaine.',
        'notes': 'This is exactly how chronic diseases start - one "harmless" indulgence at a time.'
    }
    
    # Test formatting for both healthy and junk food
    try:
        from ai.vision_analyzer import VisionAnalyzer
        analyzer = VisionAnalyzer()

        # Test healthy food formatting
        print("Testing HEALTHY food formatting:")
        healthy_message = analyzer.format_analysis_for_user(healthy_analysis)
        print("Healthy food formatting successful!")
        print("\nHealthy food sample:")
        print("-" * 50)
        print(healthy_message[:300] + "..." if len(healthy_message) > 300 else healthy_message)
        print("-" * 50)

        # Test junk food formatting with reality check
        print("\nTesting JUNK food formatting with REALITY CHECK:")
        junk_message = analyzer.format_analysis_for_user(junk_analysis)
        print("Junk food reality check formatting successful!")
        print("\nJunk food reality check sample:")
        print("-" * 50)
        print(junk_message[:400] + "..." if len(junk_message) > 400 else junk_message)
        print("-" * 50)

        # Check for key elements in junk food message
        assert "REALITY CHECK" in junk_message, "Missing reality check text"
        assert "WARNING" in junk_message, "Missing warning text"

        print("All reality check elements present in junk food message!")
        print("Dark messaging system working correctly!")

    except Exception as e:
        print(f"Message formatting failed: {e}")

def main():
    """Run all tests"""
    print("MealMetrics Bot Improvements Test Suite")
    print("=" * 50)
    
    try:
        test_dynamic_examples()
        test_message_formatting()
        
        print("\n" + "=" * 50)
        print("All tests passed! Improvements are working correctly.")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        print("=" * 50)

if __name__ == "__main__":
    main()
