#!/usr/bin/env python3
"""
Comprehensive test suite for MealMetrics bot
Tests all major components and improvements
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import sqlite3

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.helpers import (
    format_calories, get_current_date, validate_image_format,
    format_meal_summary, escape_markdown_v2, sanitize_input,
    parse_numeric_value, validate_user_input, format_confidence
)
from database.models import DatabaseManager
from database.operations import MealOperations
from ai.vision_analyzer import VisionAnalyzer

class TestHelperFunctions(unittest.TestCase):
    """Test utility helper functions"""
    
    def test_format_calories(self):
        """Test calorie formatting"""
        self.assertEqual(format_calories(100), "100 calories")
        self.assertEqual(format_calories(100.5), "100.5 calories")
        self.assertEqual(format_calories(0), "0 calories")
    
    def test_parse_numeric_value(self):
        """Test numeric value parsing"""
        self.assertEqual(parse_numeric_value("100 calories"), 100.0)
        self.assertEqual(parse_numeric_value("85%"), 85.0)
        self.assertEqual(parse_numeric_value(150), 150.0)
        self.assertEqual(parse_numeric_value("invalid", 50.0), 50.0)
        self.assertEqual(parse_numeric_value("", 25.0), 25.0)
    
    def test_escape_markdown_v2(self):
        """Test markdown escaping"""
        text = "Test_text*with[special]chars"
        escaped = escape_markdown_v2(text)
        self.assertIn("\\_", escaped)
        self.assertIn("\\*", escaped)
        self.assertIn("\\[", escaped)
        self.assertIn("\\]", escaped)
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        self.assertEqual(sanitize_input("  test  text  "), "test text")
        self.assertEqual(sanitize_input("a" * 1500, 100), "a" * 100 + "...")
        self.assertEqual(sanitize_input(""), "")
    
    def test_validate_user_input(self):
        """Test user input validation"""
        self.assertTrue(validate_user_input("valid input"))
        self.assertFalse(validate_user_input(""))
        self.assertFalse(validate_user_input("a" * 1500))
        self.assertFalse(validate_user_input(None))
    
    def test_format_confidence(self):
        """Test confidence formatting"""
        self.assertIn("Very High", format_confidence(95))
        self.assertIn("High", format_confidence(80))
        self.assertIn("Medium", format_confidence(65))
        self.assertIn("Low", format_confidence(50))
    
    def test_validate_image_format(self):
        """Test image format validation"""
        supported = ['jpg', 'jpeg', 'png', 'webp']
        self.assertTrue(validate_image_format("test.jpg", supported))
        self.assertTrue(validate_image_format("test.PNG", supported))
        self.assertFalse(validate_image_format("test.gif", supported))
        self.assertFalse(validate_image_format("", supported))

class TestConfigValidation(unittest.TestCase):
    """Test configuration validation"""
    
    def setUp(self):
        """Set up test environment"""
        # Store original values
        self.original_token = Config.TELEGRAM_BOT_TOKEN
        self.original_api_key = Config.OPENROUTER_API_KEY
    
    def tearDown(self):
        """Restore original values"""
        Config.TELEGRAM_BOT_TOKEN = self.original_token
        Config.OPENROUTER_API_KEY = self.original_api_key
    
    def test_valid_config(self):
        """Test valid configuration"""
        Config.TELEGRAM_BOT_TOKEN = "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk"
        Config.OPENROUTER_API_KEY = "sk-or-v1-1234567890abcdef"
        self.assertTrue(Config.validate())
    
    def test_missing_token(self):
        """Test missing bot token"""
        Config.TELEGRAM_BOT_TOKEN = None
        Config.OPENROUTER_API_KEY = "valid-key-here"
        with self.assertRaises(ValueError):
            Config.validate()
    
    def test_invalid_token_format(self):
        """Test invalid bot token format"""
        Config.TELEGRAM_BOT_TOKEN = "invalid-token"
        Config.OPENROUTER_API_KEY = "valid-key-here"
        with self.assertRaises(ValueError):
            Config.validate()

class TestDatabaseOperations(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.meal_ops = MealOperations(self.db_manager)
    
    def tearDown(self):
        """Clean up test database"""
        # DatabaseManager doesn't have a close method, just clean up the file
        os.unlink(self.temp_db.name)
    
    def test_log_meal(self):
        """Test meal logging"""
        user_id = 12345
        description = "Test meal"
        calories = 500.0
        confidence = 85.0
        
        # Create user first
        self.db_manager.create_user(user_id, "testuser", "Test", "User")
        
        # Log meal
        success = self.meal_ops.log_meal(user_id, description, calories, confidence)
        self.assertTrue(success)
        
        # Verify meal was logged
        meals = self.meal_ops.get_user_meals_today(user_id)
        self.assertEqual(len(meals), 1)
        self.assertEqual(meals[0]['description'], description)
        self.assertEqual(meals[0]['calories'], calories)
    
    def test_get_user_stats(self):
        """Test user statistics"""
        user_id = 12345
        
        # Create user
        self.db_manager.create_user(user_id, "testuser", "Test", "User")
        
        # Log some meals
        self.meal_ops.log_meal(user_id, "Breakfast", 300, 80)
        self.meal_ops.log_meal(user_id, "Lunch", 500, 85)
        
        # Get stats
        stats = self.meal_ops.get_user_stats(user_id, days=7)
        self.assertEqual(stats['total_meals'], 2)
        self.assertEqual(stats['total_calories'], 800)
        self.assertEqual(stats['days_tracked'], 1)

class TestVisionAnalyzer(unittest.TestCase):
    """Test vision analyzer functionality"""
    
    def setUp(self):
        """Set up vision analyzer"""
        self.analyzer = VisionAnalyzer()
    
    def test_format_analysis_for_user(self):
        """Test analysis formatting"""
        analysis = {
            'description': 'Test meal',
            'total_calories': 500,
            'confidence': 85,
            'health_category': 'healthy',
            'health_score': 8,
            'witty_comment': 'Great choice!',
            'recommendations': 'Keep it up!'
        }
        
        formatted = self.analyzer.format_analysis_for_user(analysis)
        self.assertIn('Test meal', formatted)
        self.assertIn('500', formatted)
        self.assertIn('85%', formatted)
        self.assertIn('Great choice!', formatted)
    
    def test_format_analysis_junk_food(self):
        """Test junk food analysis formatting"""
        analysis = {
            'description': 'Large pizza',
            'total_calories': 1200,
            'confidence': 90,
            'health_category': 'junk',
            'health_score': 2,
            'witty_comment': 'This is not helping your health goals',
            'recommendations': 'Consider healthier alternatives'
        }
        
        formatted = self.analyzer.format_analysis_for_user(analysis)
        self.assertIn('WARNING', formatted)
        self.assertIn('DANGER ZONE', formatted)
        self.assertIn('REALITY CHECK', formatted)

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("Running Comprehensive MealMetrics Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHelperFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestVisionAnalyzer))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("All tests passed! The codebase improvements are working correctly.")
    else:
        print(f"{len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        for failure in result.failures:
            print(f"FAIL: {failure[0]}")
        for error in result.errors:
            print(f"ERROR: {error[0]}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
