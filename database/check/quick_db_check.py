#!/usr/bin/env python3
"""
Quick Database Check - Simple script to view all users and their data
Run this from MealMetrics root directory
"""

import os
import sqlite3
from datetime import datetime, date

def check_database():
    """Quick check of database contents"""

    # Find database file in MealMetrics root directory
    # This script can be in database/check/ or root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Check if we're in database/check folder
    if current_dir.endswith('database/check') or current_dir.endswith('database\\check'):
        root_dir = os.path.dirname(os.path.dirname(current_dir))
    else:
        # We're in root directory
        root_dir = current_dir

    db_files = []
    for file in os.listdir(root_dir):
        if file.endswith('.db'):
            db_files.append(os.path.join(root_dir, file))
    
    if not db_files:
        print("❌ No SQLite database files found in MealMetrics root directory!")
        print("Make sure the MealMetrics database exists.")
        return

    # Use first database file found
    db_file = db_files[0]
    db_name = os.path.basename(db_file)
    print(f"📁 Using database: {db_name}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if 'users' not in tables or 'meals' not in tables:
            print("❌ Required tables not found in database!")
            print(f"Found tables: {tables}")
            return
        
        # Database overview
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM meals')
        total_meals = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(calories) FROM meals')
        total_calories = cursor.fetchone()[0] or 0
        
        print("📊 DATABASE OVERVIEW")
        print("-" * 30)
        print(f"👥 Total Users: {total_users}")
        print(f"🍽️ Total Meals: {total_meals}")
        print(f"🔥 Total Calories: {total_calories:,.0f}")
        print()
        
        if total_users == 0:
            print("ℹ️  No users found in database.")
            return
        
        # Get all users with their data
        cursor.execute('''
            SELECT u.user_id, u.username, u.first_name, u.last_name, u.last_active,
                   COUNT(m.id) as meal_count,
                   COALESCE(SUM(m.calories), 0) as total_calories,
                   COUNT(DISTINCT m.date) as days_tracked
            FROM users u
            LEFT JOIN meals m ON u.user_id = m.user_id
            GROUP BY u.user_id
            ORDER BY u.last_active DESC
        ''')
        
        users_data = cursor.fetchall()
        
        print("👥 ALL USERS:")
        print("=" * 60)
        
        for i, user_data in enumerate(users_data, 1):
            user_id, username, first_name, last_name, last_active, meal_count, calories, days = user_data
            
            # Format name
            name = f"{first_name or ''} {last_name or ''}".strip()
            if not name:
                name = username or "Unknown"
            
            # Format last active
            try:
                last_active_dt = datetime.fromisoformat(last_active)
                days_ago = (datetime.now() - last_active_dt).days
                if days_ago == 0:
                    activity = "🟢 Today"
                elif days_ago <= 7:
                    activity = f"🟡 {days_ago}d ago"
                else:
                    activity = f"🔴 {days_ago}d ago"
            except:
                activity = "❓ Unknown"
            
            print(f"{i:2d}. {name} (@{username or 'N/A'})")
            print(f"    ID: {user_id}")
            print(f"    Activity: {activity}")
            print(f"    Meals: {meal_count} | Calories: {calories:,.0f} | Days: {days}")
            
            # Show recent meals for this user
            cursor.execute('''
                SELECT description, calories, timestamp
                FROM meals 
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 3
            ''', (user_id,))
            
            recent_meals = cursor.fetchall()
            if recent_meals:
                print("    Recent meals:")
                for meal in recent_meals:
                    desc = meal[0][:30] + "..." if len(meal[0]) > 30 else meal[0]
                    try:
                        time_str = datetime.fromisoformat(meal[2]).strftime("%m/%d %H:%M")
                    except:
                        time_str = "Unknown"
                    print(f"      • {desc} - {meal[1]:.0f} cal ({time_str})")
            else:
                print("    No meals logged yet")
            
            print()
        
        # Today's activity
        today = date.today().isoformat()
        cursor.execute('''
            SELECT u.username, u.first_name, COUNT(m.id), SUM(m.calories)
            FROM users u
            JOIN meals m ON u.user_id = m.user_id
            WHERE m.date = ?
            GROUP BY u.user_id
        ''', (today,))
        
        today_activity = cursor.fetchall()
        
        if today_activity:
            print("📅 TODAY'S ACTIVITY:")
            print("-" * 30)
            for activity in today_activity:
                username, first_name, meal_count, calories = activity
                name = first_name or username or "Unknown"
                print(f"• {name}: {meal_count} meals, {calories:,.0f} calories")
        else:
            print("📅 No activity today yet.")
        
        conn.close()
        print("\n✅ Database check complete!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🔍 MEALMETRICS QUICK DATABASE CHECK")
    print("=" * 60)
    
    # Check if MealMetrics root directory exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir.endswith('database/check') or current_dir.endswith('database\\check'):
        root_dir = os.path.dirname(os.path.dirname(current_dir))
    else:
        root_dir = current_dir

    if not os.path.exists(os.path.join(root_dir, 'main.py')) or not os.path.exists(os.path.join(root_dir, 'utils')):
        print("⚠️  Warning: Cannot find MealMetrics root directory.")
        print(f"Looking in: {root_dir}")
        print("Make sure this script is in the database/check folder or MealMetrics root.")
        print()
    
    check_database()

if __name__ == "__main__":
    main()
