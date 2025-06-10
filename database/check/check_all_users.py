#!/usr/bin/env python3
"""
MealMetrics Database User Data Checker
Organized view of all users and their data
"""

import os
import sys
import sqlite3
from datetime import datetime, date, timedelta
from typing import Dict, List, Any
import json

# Add MealMetrics root directory to path for imports
# We're in database/check, so go up two levels to reach MealMetrics root
current_dir = os.path.dirname(os.path.abspath(__file__))  # database/check
database_dir = os.path.dirname(current_dir)              # database
root_dir = os.path.dirname(database_dir)                 # MealMetrics
sys.path.insert(0, root_dir)

try:
    from utils.config import Config
    from database.models import DatabaseManager
    from database.operations import MealOperations
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the MealMetrics/database/check directory")
    print("Or run from MealMetrics root: python database/check/check_all_users.py")
    sys.exit(1)

class UserDataChecker:
    """Check and display all users' data in organized format"""
    
    def __init__(self):
        """Initialize database connection"""
        try:
            # Try to use configured database
            if Config.DATABASE_TYPE == 'sqlite':
                # Make sure database path is relative to MealMetrics root
                db_path = Config.DATABASE_PATH
                if not os.path.isabs(db_path):
                    # Get MealMetrics root directory
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    database_dir = os.path.dirname(current_dir)
                    root_dir = os.path.dirname(database_dir)
                    db_path = os.path.join(root_dir, db_path)

                self.db = DatabaseManager(db_path)
                self.db_type = 'sqlite'
                print(f"📁 Connected to SQLite database: {os.path.basename(db_path)}")
            else:
                print("⚠️  MySQL database detected. This script works with SQLite only.")
                print("Please check your .env file or use SQLite for this script.")
                sys.exit(1)
                
            self.meal_ops = MealOperations(self.db)
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("Make sure your database file exists and is accessible.")
            sys.exit(1)
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users from database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, username, first_name, last_name, created_at, last_active
                    FROM users 
                    ORDER BY last_active DESC
                ''')
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'user_id': row[0],
                        'username': row[1] or 'N/A',
                        'first_name': row[2] or 'N/A',
                        'last_name': row[3] or 'N/A',
                        'created_at': row[4],
                        'last_active': row[5]
                    })
                
                return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive stats for a user"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total meals
                cursor.execute('SELECT COUNT(*) FROM meals WHERE user_id = ?', (user_id,))
                total_meals = cursor.fetchone()[0]
                
                # Total calories
                cursor.execute('SELECT SUM(calories) FROM meals WHERE user_id = ?', (user_id,))
                total_calories = cursor.fetchone()[0] or 0
                
                # Days with data
                cursor.execute('SELECT COUNT(DISTINCT date) FROM meals WHERE user_id = ?', (user_id,))
                days_tracked = cursor.fetchone()[0]
                
                # First and last meal dates
                cursor.execute('''
                    SELECT MIN(date), MAX(date) 
                    FROM meals WHERE user_id = ?
                ''', (user_id,))
                date_range = cursor.fetchone()
                first_meal_date = date_range[0] if date_range[0] else 'N/A'
                last_meal_date = date_range[1] if date_range[1] else 'N/A'
                
                # Recent meals (last 5)
                cursor.execute('''
                    SELECT description, calories, timestamp 
                    FROM meals 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                ''', (user_id,))
                recent_meals = cursor.fetchall()
                
                # Today's meals
                today = date.today().isoformat()
                cursor.execute('''
                    SELECT COUNT(*), COALESCE(SUM(calories), 0)
                    FROM meals 
                    WHERE user_id = ? AND date = ?
                ''', (user_id, today))
                today_data = cursor.fetchone()
                today_meals = today_data[0]
                today_calories = today_data[1]
                
                # Pending meals
                cursor.execute('SELECT COUNT(*) FROM pending_meals WHERE user_id = ?', (user_id,))
                pending_meals = cursor.fetchone()[0]
                
                return {
                    'total_meals': total_meals,
                    'total_calories': total_calories,
                    'days_tracked': days_tracked,
                    'first_meal_date': first_meal_date,
                    'last_meal_date': last_meal_date,
                    'recent_meals': recent_meals,
                    'today_meals': today_meals,
                    'today_calories': today_calories,
                    'pending_meals': pending_meals,
                    'avg_calories_per_day': total_calories / max(days_tracked, 1)
                }
        except Exception as e:
            print(f"Error getting stats for user {user_id}: {e}")
            return {}
    
    def format_user_display(self, user: Dict[str, Any], stats: Dict[str, Any]) -> str:
        """Format user data for display"""
        # User info
        display_name = f"{user['first_name']} {user['last_name']}".strip()
        if display_name == "N/A N/A":
            display_name = user['username']
        
        # Activity status
        try:
            last_active = datetime.fromisoformat(user['last_active'])
            days_since_active = (datetime.now() - last_active).days
            if days_since_active == 0:
                activity_status = "🟢 Active today"
            elif days_since_active <= 7:
                activity_status = f"🟡 Active {days_since_active} days ago"
            else:
                activity_status = f"🔴 Inactive ({days_since_active} days)"
        except:
            activity_status = "❓ Unknown"
        
        # Format output
        output = f"""
┌─ 👤 USER: {display_name} (@{user['username']})
├─ 🆔 ID: {user['user_id']}
├─ {activity_status}
├─ 📊 STATISTICS:
│  ├─ Total Meals: {stats['total_meals']}
│  ├─ Total Calories: {stats['total_calories']:,.0f}
│  ├─ Days Tracked: {stats['days_tracked']}
│  ├─ Avg Calories/Day: {stats['avg_calories_per_day']:,.0f}
│  └─ Date Range: {stats['first_meal_date']} → {stats['last_meal_date']}
├─ 📅 TODAY:
│  ├─ Meals: {stats['today_meals']}
│  ├─ Calories: {stats['today_calories']:,.0f}
│  └─ Pending: {stats['pending_meals']}
└─ 🍽️ RECENT MEALS:"""
        
        # Add recent meals
        if stats['recent_meals']:
            for i, meal in enumerate(stats['recent_meals'], 1):
                desc = meal[0][:40] + "..." if len(meal[0]) > 40 else meal[0]
                calories = meal[1]
                timestamp = meal[2]
                try:
                    time_str = datetime.fromisoformat(timestamp).strftime("%m/%d %H:%M")
                except:
                    time_str = "Unknown"
                output += f"\n   {i}. {desc} - {calories:.0f} cal ({time_str})"
        else:
            output += "\n   No meals logged yet"
        
        return output
    
    def display_database_overview(self):
        """Display overall database statistics"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Overall stats
                cursor.execute('SELECT COUNT(*) FROM users')
                total_users = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM meals')
                total_meals = cursor.fetchone()[0]
                
                cursor.execute('SELECT SUM(calories) FROM meals')
                total_calories = cursor.fetchone()[0] or 0
                
                cursor.execute('SELECT COUNT(*) FROM pending_meals')
                total_pending = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(DISTINCT date) FROM meals')
                unique_dates = cursor.fetchone()[0]
                
                # Active users (last 7 days)
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                cursor.execute('SELECT COUNT(*) FROM users WHERE last_active >= ?', (week_ago,))
                active_users = cursor.fetchone()[0]
                
                print("=" * 60)
                print("📊 MEALMETRICS DATABASE OVERVIEW")
                print("=" * 60)
                print(f"👥 Total Users: {total_users}")
                print(f"🟢 Active Users (7 days): {active_users}")
                print(f"🍽️ Total Meals Logged: {total_meals:,}")
                print(f"🔥 Total Calories Tracked: {total_calories:,.0f}")
                print(f"⏳ Pending Meals: {total_pending}")
                print(f"📅 Days with Data: {unique_dates}")
                if total_meals > 0:
                    print(f"📈 Avg Calories per Meal: {total_calories/total_meals:.0f}")
                print("=" * 60)
                
        except Exception as e:
            print(f"Error getting database overview: {e}")
    
    def check_all_users(self, detailed: bool = True):
        """Main function to check all users"""
        print("🔍 CHECKING ALL USERS DATA...")
        print()
        
        # Database overview
        self.display_database_overview()
        
        # Get all users
        users = self.get_all_users()
        
        if not users:
            print("❌ No users found in database!")
            return
        
        print(f"\n👥 FOUND {len(users)} USERS:")
        print("=" * 60)
        
        for i, user in enumerate(users, 1):
            if detailed:
                stats = self.get_user_stats(user['user_id'])
                print(self.format_user_display(user, stats))
                if i < len(users):
                    print("\n" + "─" * 60)
            else:
                # Simple format
                display_name = f"{user['first_name']} {user['last_name']}".strip()
                if display_name == "N/A N/A":
                    display_name = user['username']
                print(f"{i:2d}. {display_name} (@{user['username']}) - ID: {user['user_id']}")
        
        print("\n" + "=" * 60)
        print("✅ USER DATA CHECK COMPLETE")

def main():
    """Main function with command line options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check MealMetrics database users')
    parser.add_argument('--simple', action='store_true', help='Show simple user list only')
    parser.add_argument('--export', type=str, help='Export data to JSON file')
    
    args = parser.parse_args()
    
    try:
        checker = UserDataChecker()
        
        if args.export:
            # Export functionality
            users = checker.get_all_users()
            export_data = []
            
            for user in users:
                stats = checker.get_user_stats(user['user_id'])
                export_data.append({
                    'user': user,
                    'stats': stats
                })
            
            with open(args.export, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            print(f"📁 Data exported to: {args.export}")
        else:
            # Regular check
            checker.check_all_users(detailed=not args.simple)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Check cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
