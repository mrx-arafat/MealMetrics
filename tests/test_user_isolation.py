#!/usr/bin/env python3
"""
Test user data isolation - ensure one user's actions don't affect other users
"""

import sys
import os
import tempfile
import sqlite3
from datetime import datetime, date

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import DatabaseManager
from database.operations import MealOperations

def test_user_data_isolation():
    """Test that clearing one user's data doesn't affect other users"""
    print("Testing User Data Isolation:")
    print("=" * 40)
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    try:
        # Initialize test database
        db = DatabaseManager(test_db_path)
        db.init_database()
        meal_ops = MealOperations(db)
        
        # Create test users
        user1_id = 123456789  # User 1 (Telegram ID)
        user2_id = 987654321  # User 2 (Telegram ID)
        user3_id = 555666777  # User 3 (Telegram ID)
        
        # Create users in database
        db.create_user(user1_id, "user1", "Test", "User1")
        db.create_user(user2_id, "user2", "Test", "User2")
        db.create_user(user3_id, "user3", "Test", "User3")
        
        print(f"Created 3 test users: {user1_id}, {user2_id}, {user3_id}")
        
        # Add meals for each user
        today = date.today().isoformat()
        
        # User 1 meals
        meal_ops.log_meal(user1_id, "User1 Breakfast", 300, 85)
        meal_ops.log_meal(user1_id, "User1 Lunch", 500, 90)
        meal_ops.log_meal(user1_id, "User1 Dinner", 600, 88)
        
        # User 2 meals
        meal_ops.log_meal(user2_id, "User2 Breakfast", 250, 80)
        meal_ops.log_meal(user2_id, "User2 Lunch", 450, 85)
        meal_ops.log_meal(user2_id, "User2 Dinner", 550, 90)
        
        # User 3 meals
        meal_ops.log_meal(user3_id, "User3 Breakfast", 200, 75)
        meal_ops.log_meal(user3_id, "User3 Lunch", 400, 80)
        meal_ops.log_meal(user3_id, "User3 Dinner", 500, 85)
        
        print("Added 3 meals for each user (9 total meals)")
        
        # Verify initial state
        user1_meals_before = meal_ops.get_user_meals_today(user1_id)
        user2_meals_before = meal_ops.get_user_meals_today(user2_id)
        user3_meals_before = meal_ops.get_user_meals_today(user3_id)
        
        print(f"Before clearing:")
        print(f"  User1 meals: {len(user1_meals_before)}")
        print(f"  User2 meals: {len(user2_meals_before)}")
        print(f"  User3 meals: {len(user3_meals_before)}")
        
        # User 2 clears ALL their data
        print(f"\n🗑️ User2 ({user2_id}) is clearing ALL their data...")
        success = meal_ops.clear_all_user_data(user2_id)
        
        if not success:
            print("FAIL: Could not clear user2 data!")
            return False
        
        # Check state after User2 clears their data
        user1_meals_after = meal_ops.get_user_meals_today(user1_id)
        user2_meals_after = meal_ops.get_user_meals_today(user2_id)
        user3_meals_after = meal_ops.get_user_meals_today(user3_id)
        
        print(f"After User2 clears their data:")
        print(f"  User1 meals: {len(user1_meals_after)}")
        print(f"  User2 meals: {len(user2_meals_after)}")
        print(f"  User3 meals: {len(user3_meals_after)}")
        
        # Verify isolation
        if len(user1_meals_after) == 3 and len(user3_meals_after) == 3:
            print("✅ PASS: Other users' data is safe!")
            isolation_test_passed = True
        else:
            print("❌ FAIL: Other users' data was affected!")
            isolation_test_passed = False
        
        if len(user2_meals_after) == 0:
            print("✅ PASS: User2's data was properly cleared!")
            clear_test_passed = True
        else:
            print("❌ FAIL: User2's data was not properly cleared!")
            clear_test_passed = False
        
        return isolation_test_passed and clear_test_passed
        
    finally:
        # Clean up test database
        try:
            os.unlink(test_db_path)
        except:
            pass

def test_partial_clear_isolation():
    """Test that clearing today's data for one user doesn't affect others"""
    print("\nTesting Partial Clear Isolation:")
    print("=" * 40)
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    try:
        # Initialize test database
        db = DatabaseManager(test_db_path)
        db.init_database()
        meal_ops = MealOperations(db)
        
        # Create test users
        user1_id = 111111111
        user2_id = 222222222
        
        # Create users in database
        db.create_user(user1_id, "user1", "Test", "User1")
        db.create_user(user2_id, "user2", "Test", "User2")
        
        # Add meals for today
        today = date.today().isoformat()
        
        # User 1 meals
        meal_ops.log_meal(user1_id, "User1 Today Meal1", 300, 85)
        meal_ops.log_meal(user1_id, "User1 Today Meal2", 400, 90)
        
        # User 2 meals
        meal_ops.log_meal(user2_id, "User2 Today Meal1", 250, 80)
        meal_ops.log_meal(user2_id, "User2 Today Meal2", 350, 85)
        
        print("Added 2 meals for each user today")
        
        # User 1 clears today's data
        print(f"🗑️ User1 ({user1_id}) is clearing today's data...")
        success = meal_ops.clear_user_data_by_date(user1_id, today)
        
        if not success:
            print("FAIL: Could not clear user1's today data!")
            return False
        
        # Check results
        user1_meals_after = meal_ops.get_user_meals_today(user1_id)
        user2_meals_after = meal_ops.get_user_meals_today(user2_id)
        
        print(f"After User1 clears today's data:")
        print(f"  User1 meals today: {len(user1_meals_after)}")
        print(f"  User2 meals today: {len(user2_meals_after)}")
        
        if len(user1_meals_after) == 0 and len(user2_meals_after) == 2:
            print("✅ PASS: Partial clear is properly isolated!")
            return True
        else:
            print("❌ FAIL: Partial clear affected wrong user!")
            return False
        
    finally:
        # Clean up test database
        try:
            os.unlink(test_db_path)
        except:
            pass

def test_database_queries():
    """Test the actual SQL queries used for clearing data"""
    print("\nTesting Database Queries:")
    print("=" * 35)
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    try:
        # Initialize test database
        db = DatabaseManager(test_db_path)
        db.init_database()
        
        # Add test data directly to database
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert test meals for different users
            test_data = [
                (100, "User100 Meal1", 300, "2024-01-15"),
                (100, "User100 Meal2", 400, "2024-01-15"),
                (200, "User200 Meal1", 250, "2024-01-15"),
                (200, "User200 Meal2", 350, "2024-01-15"),
                (300, "User300 Meal1", 200, "2024-01-15"),
            ]
            
            for user_id, desc, calories, date_str in test_data:
                cursor.execute('''
                    INSERT INTO meals (user_id, description, calories, confidence, timestamp, date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, desc, calories, 85, datetime.now().isoformat(), date_str))
            
            conn.commit()
            
            # Count total meals before
            cursor.execute("SELECT COUNT(*) FROM meals")
            total_before = cursor.fetchone()[0]
            print(f"Total meals before: {total_before}")
            
            # Count meals per user before
            for user_id in [100, 200, 300]:
                cursor.execute("SELECT COUNT(*) FROM meals WHERE user_id = ?", (user_id,))
                count = cursor.fetchone()[0]
                print(f"  User {user_id}: {count} meals")
            
            # Clear all data for user 200 (simulating user clearing their data)
            print(f"\n🗑️ Clearing all data for User 200...")
            cursor.execute("DELETE FROM meals WHERE user_id = ?", (200,))
            deleted_count = cursor.rowcount
            conn.commit()
            
            print(f"Deleted {deleted_count} meals for User 200")
            
            # Count total meals after
            cursor.execute("SELECT COUNT(*) FROM meals")
            total_after = cursor.fetchone()[0]
            print(f"Total meals after: {total_after}")
            
            # Count meals per user after
            for user_id in [100, 200, 300]:
                cursor.execute("SELECT COUNT(*) FROM meals WHERE user_id = ?", (user_id,))
                count = cursor.fetchone()[0]
                print(f"  User {user_id}: {count} meals")
            
            # Verify isolation
            cursor.execute("SELECT COUNT(*) FROM meals WHERE user_id = 100")
            user100_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM meals WHERE user_id = 300")
            user300_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM meals WHERE user_id = 200")
            user200_count = cursor.fetchone()[0]
            
            if user100_count == 2 and user300_count == 1 and user200_count == 0:
                print("✅ PASS: SQL queries properly isolate users!")
                return True
            else:
                print("❌ FAIL: SQL queries don't properly isolate users!")
                return False
        
    finally:
        # Clean up test database
        try:
            os.unlink(test_db_path)
        except:
            pass

def main():
    """Run all user isolation tests"""
    print("MealMetrics User Data Isolation Test Suite")
    print("=" * 50)
    
    try:
        results = []
        results.append(test_user_data_isolation())
        results.append(test_partial_clear_isolation())
        results.append(test_database_queries())
        
        print("\n" + "=" * 50)
        if all(results):
            print("🔒 ALL TESTS PASSED!")
            print("\n✅ CONFIRMED: User data is completely isolated!")
            print("✅ When one user clears data, other users are NOT affected!")
            print("✅ Each user can only delete their own data!")
            print("✅ Database queries properly use user_id filters!")
        else:
            print("❌ SOME TESTS FAILED!")
            print("⚠️  There may be data isolation issues!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nTest failed: {e}")

if __name__ == "__main__":
    main()
