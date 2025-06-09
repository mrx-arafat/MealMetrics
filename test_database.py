#!/usr/bin/env python3
"""
Test database connection for MealMetrics bot (SQLite or MySQL)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config import Config
from database.factory import create_database_manager

def test_database_connection():
    """Test the database connection"""
    print("🔧 Testing Database Connection...")
    print("=" * 50)
    
    try:
        # Load configuration
        config = Config()
        print(f"📊 Database Type: {config.DATABASE_TYPE}")
        
        if config.DATABASE_TYPE == 'sqlite':
            print(f"📁 SQLite Database: {config.DATABASE_PATH}")
        else:
            print(f"🌐 MySQL Host: {config.MYSQL_HOST}")
            print(f"🔌 MySQL Port: {config.MYSQL_PORT}")
            print(f"👤 MySQL User: {config.MYSQL_USER}")
            print(f"🗄️ MySQL Database: {config.MYSQL_DATABASE}")
        print()
        
        # Test connection
        print("🔄 Creating database manager...")
        db_manager = create_database_manager()
        print("✅ Database manager created successfully!")
        
        # Test database initialization
        print("🔄 Initializing database...")
        db_manager.init_database()
        print("✅ Database initialized successfully!")
        
        # Test user creation
        print("🔄 Testing user operations...")
        success = db_manager.create_user(
            user_id=123456789,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        
        if success:
            print("✅ User creation test passed!")
        else:
            print("❌ User creation test failed!")
        
        # Test pending meal
        print("🔄 Testing pending meal...")
        meal_id = db_manager.add_pending_meal(
            user_id=123456789,
            description="Test meal analysis",
            calories=500.0,
            confidence=0.85,
            image_path="test_image.jpg"
        )

        if meal_id:
            print(f"✅ Pending meal added successfully! ID: {meal_id}")

            # Test retrieving pending meal
            pending_meal = db_manager.get_pending_meal(123456789, meal_id)
            if pending_meal:
                print(f"✅ Pending meal retrieved: {pending_meal['description']}")
            else:
                print("❌ Pending meal retrieval failed!")
        else:
            print("❌ Pending meal creation failed!")

        # Test meal operations
        print("🔄 Testing meal operations...")
        from database.operations import MealOperations
        meal_ops = MealOperations(db_manager)

        # Test daily summary
        from datetime import date
        summary = meal_ops.get_daily_summary(123456789, date.today().isoformat())
        if summary is not None:
            print(f"✅ Daily summary retrieved: {summary.get('total_calories', 0)} calories")
        else:
            print("✅ Daily summary empty (expected for new user)")
        
        print()
        print("🎉 All database tests passed!")
        print("🚀 Your database is ready for MealMetrics!")
        print("🚀 You can now run the bot with: python main.py")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        print()
        print("🔧 Troubleshooting tips:")
        if config.DATABASE_TYPE == 'mysql':
            print("1. Check if MySQL server is running")
            print("2. Verify your credentials in .env file")
            print("3. Ensure the database user has proper permissions")
            print("4. Check if the host/port is accessible")
        else:
            print("1. Check if the SQLite database file is writable")
            print("2. Ensure the directory has proper permissions")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
