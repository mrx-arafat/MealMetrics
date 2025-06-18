from datetime import datetime, date, timezone, timedelta
from typing import Optional, List, Dict, Any
import logging
from .models import DatabaseManager

logger = logging.getLogger(__name__)

class MealOperations:
    """Operations for meal-related database functions"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def log_meal(self, user_id: int, description: str, calories: float,
                 confidence: float = None, image_path: str = None) -> bool:
        """Log a confirmed meal to the database"""
        # Input validation
        if not description or not isinstance(description, str):
            logger.error(f"Invalid description for user {user_id}: {description}")
            return False

        if len(description.strip()) == 0:
            logger.error(f"Empty description for user {user_id}")
            return False

        if len(description) > 1000:  # Reasonable limit
            logger.warning(f"Description too long for user {user_id}, truncating")
            description = description[:1000]

        if not isinstance(calories, (int, float)) or calories < 0:
            logger.error(f"Invalid calories for user {user_id}: {calories}")
            return False

        if calories > 10000:  # Reasonable upper limit
            logger.warning(f"Calories seem too high for user {user_id}: {calories}")

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # Use Bangladesh timezone (UTC+6)
                bangladesh_tz = timezone(timedelta(hours=6))
                now = datetime.now(bangladesh_tz)
                today = now.date().isoformat()  # Use Bangladesh date, not server date
                
                # Insert meal
                cursor.execute('''
                    INSERT INTO meals 
                    (user_id, description, calories, confidence, image_path, timestamp, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, description, calories, confidence, image_path, now.isoformat(), today))
                
                # Update daily summary
                self._update_daily_summary(cursor, user_id, today, calories)
                
                conn.commit()
                logger.info(f"Meal logged for user {user_id}: {description} ({calories} cal)")
                return True
                
        except Exception as e:
            logger.error(f"Error logging meal for user {user_id}: {e}")
            return False
    
    def _update_daily_summary(self, cursor, user_id: int, date_str: str, calories: float):
        """Update or create daily summary"""
        # Check if summary exists
        cursor.execute(
            'SELECT total_calories, meal_count FROM daily_summaries WHERE user_id = ? AND date = ?',
            (user_id, date_str)
        )
        result = cursor.fetchone()

        # Use Bangladesh timezone (UTC+6)
        bangladesh_tz = timezone(timedelta(hours=6))
        now = datetime.now(bangladesh_tz).isoformat()
        
        if result:
            # Update existing summary
            new_total = result[0] + calories
            new_count = result[1] + 1
            cursor.execute('''
                UPDATE daily_summaries 
                SET total_calories = ?, meal_count = ?, updated_at = ?
                WHERE user_id = ? AND date = ?
            ''', (new_total, new_count, now, user_id, date_str))
        else:
            # Create new summary
            cursor.execute('''
                INSERT INTO daily_summaries 
                (user_id, date, total_calories, meal_count, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, date_str, calories, 1, now, now))
    
    def get_user_meals_today(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all meals for a user today"""
        try:
            # Use Bangladesh timezone (UTC+6)
            bangladesh_tz = timezone(timedelta(hours=6))
            today = datetime.now(bangladesh_tz).date().isoformat()
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM meals 
                    WHERE user_id = ? AND date = ? 
                    ORDER BY timestamp DESC
                ''', (user_id, today))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting today's meals for user {user_id}: {e}")
            return []
    
    def get_user_meals_by_date(self, user_id: int, date_str: str) -> List[Dict[str, Any]]:
        """Get all meals for a user on a specific date"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM meals 
                    WHERE user_id = ? AND date = ? 
                    ORDER BY timestamp DESC
                ''', (user_id, date_str))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting meals for user {user_id} on {date_str}: {e}")
            return []
    
    def get_daily_summary(self, user_id: int, date_str: str = None) -> Optional[Dict[str, Any]]:
        """Get daily summary for a user"""
        if not date_str:
            # Use Bangladesh timezone (UTC+6)
            bangladesh_tz = timezone(timedelta(hours=6))
            date_str = datetime.now(bangladesh_tz).date().isoformat()
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM daily_summaries WHERE user_id = ? AND date = ?',
                    (user_id, date_str)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting daily summary for user {user_id} on {date_str}: {e}")
            return None
    
    def get_user_stats(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """Get user statistics for the last N days"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get daily summaries for the last N days
                cursor.execute('''
                    SELECT * FROM daily_summaries 
                    WHERE user_id = ? 
                    ORDER BY date DESC 
                    LIMIT ?
                ''', (user_id, days))
                
                summaries = [dict(row) for row in cursor.fetchall()]
                
                if not summaries:
                    return {
                        'total_calories': 0,
                        'total_meals': 0,
                        'avg_calories_per_day': 0,
                        'avg_meals_per_day': 0,
                        'days_tracked': 0
                    }
                
                total_calories = sum(s['total_calories'] for s in summaries)
                total_meals = sum(s['meal_count'] for s in summaries)
                days_tracked = len(summaries)
                
                return {
                    'total_calories': total_calories,
                    'total_meals': total_meals,
                    'avg_calories_per_day': total_calories / days_tracked if days_tracked > 0 else 0,
                    'avg_meals_per_day': total_meals / days_tracked if days_tracked > 0 else 0,
                    'days_tracked': days_tracked,
                    'daily_summaries': summaries
                }
                
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return {}

    def clear_user_data_by_date(self, user_id: int, date_str: str) -> bool:
        """Clear all meals and daily summary for a specific date"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Delete meals for the date
                cursor.execute(
                    'DELETE FROM meals WHERE user_id = ? AND date = ?',
                    (user_id, date_str)
                )
                meals_deleted = cursor.rowcount

                # Delete daily summary for the date
                cursor.execute(
                    'DELETE FROM daily_summaries WHERE user_id = ? AND date = ?',
                    (user_id, date_str)
                )
                summary_deleted = cursor.rowcount

                conn.commit()
                logger.info(f"Cleared data for user {user_id} on {date_str}: {meals_deleted} meals, {summary_deleted} summary")
                return True

        except Exception as e:
            logger.error(f"Error clearing data for user {user_id} on {date_str}: {e}")
            return False

    def clear_user_data_range(self, user_id: int, start_date: str, end_date: str) -> bool:
        """Clear all meals and daily summaries for a date range"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Delete meals in date range
                cursor.execute(
                    'DELETE FROM meals WHERE user_id = ? AND date >= ? AND date <= ?',
                    (user_id, start_date, end_date)
                )
                meals_deleted = cursor.rowcount

                # Delete daily summaries in date range
                cursor.execute(
                    'DELETE FROM daily_summaries WHERE user_id = ? AND date >= ? AND date <= ?',
                    (user_id, start_date, end_date)
                )
                summaries_deleted = cursor.rowcount

                conn.commit()
                logger.info(f"Cleared data for user {user_id} from {start_date} to {end_date}: {meals_deleted} meals, {summaries_deleted} summaries")
                return True

        except Exception as e:
            logger.error(f"Error clearing data range for user {user_id}: {e}")
            return False

    def clear_all_user_data(self, user_id: int) -> bool:
        """Clear ALL data for a user (use with caution!)"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Delete all meals
                cursor.execute('DELETE FROM meals WHERE user_id = ?', (user_id,))
                meals_deleted = cursor.rowcount

                # Delete all daily summaries
                cursor.execute('DELETE FROM daily_summaries WHERE user_id = ?', (user_id,))
                summaries_deleted = cursor.rowcount

                # Delete any pending meals
                cursor.execute('DELETE FROM pending_meals WHERE user_id = ?', (user_id,))
                pending_deleted = cursor.rowcount

                conn.commit()
                logger.info(f"Cleared ALL data for user {user_id}: {meals_deleted} meals, {summaries_deleted} summaries, {pending_deleted} pending")
                return True

        except Exception as e:
            logger.error(f"Error clearing all data for user {user_id}: {e}")
            return False

    def get_user_data_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary of user's stored data"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Count total meals
                cursor.execute('SELECT COUNT(*) FROM meals WHERE user_id = ?', (user_id,))
                total_meals = cursor.fetchone()[0]

                # Count days with data
                cursor.execute('SELECT COUNT(DISTINCT date) FROM meals WHERE user_id = ?', (user_id,))
                days_with_data = cursor.fetchone()[0]

                # Get date range
                cursor.execute(
                    'SELECT MIN(date), MAX(date) FROM meals WHERE user_id = ?',
                    (user_id,)
                )
                date_range = cursor.fetchone()

                # Get total calories
                cursor.execute('SELECT SUM(calories) FROM meals WHERE user_id = ?', (user_id,))
                total_calories = cursor.fetchone()[0] or 0

                return {
                    'total_meals': total_meals,
                    'days_with_data': days_with_data,
                    'first_meal_date': date_range[0],
                    'last_meal_date': date_range[1],
                    'total_calories': total_calories
                }

        except Exception as e:
            logger.error(f"Error getting data summary for user {user_id}: {e}")
            return {}
