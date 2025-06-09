import sqlite3
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for MealMetrics bot"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        return conn
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TEXT NOT NULL,
                    last_active TEXT NOT NULL
                )
            ''')
            
            # Meals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    calories REAL NOT NULL,
                    confidence REAL,
                    image_path TEXT,
                    timestamp TEXT NOT NULL,
                    date TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Daily summaries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    total_calories REAL NOT NULL,
                    meal_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(user_id, date),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Pending meals table (for log/cancel functionality)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pending_meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    calories REAL NOT NULL,
                    confidence REAL,
                    image_path TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def create_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> bool:
        """Create or update user in database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, created_at, last_active)
                    VALUES (?, ?, ?, ?, 
                        COALESCE((SELECT created_at FROM users WHERE user_id = ?), ?), 
                        ?)
                ''', (user_id, username, first_name, last_name, user_id, now, now))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating/updating user {user_id}: {e}")
            return False
    
    def update_user_activity(self, user_id: int) -> bool:
        """Update user's last activity timestamp"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE users SET last_active = ? WHERE user_id = ?',
                    (datetime.now().isoformat(), user_id)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating user activity for {user_id}: {e}")
            return False

    def add_pending_meal(self, user_id: int, description: str, calories: float,
                        confidence: float = None, image_path: str = None) -> Optional[int]:
        """Add a pending meal (waiting for user confirmation)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO pending_meals
                    (user_id, description, calories, confidence, image_path, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, description, calories, confidence, image_path, datetime.now().isoformat()))

                meal_id = cursor.lastrowid
                conn.commit()
                return meal_id
        except Exception as e:
            logger.error(f"Error adding pending meal for user {user_id}: {e}")
            return None

    def get_pending_meal(self, user_id: int, meal_id: int) -> Optional[Dict[str, Any]]:
        """Get a pending meal by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM pending_meals WHERE user_id = ? AND id = ?',
                    (user_id, meal_id)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting pending meal {meal_id} for user {user_id}: {e}")
            return None

    def delete_pending_meal(self, user_id: int, meal_id: int) -> bool:
        """Delete a pending meal"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'DELETE FROM pending_meals WHERE user_id = ? AND id = ?',
                    (user_id, meal_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting pending meal {meal_id} for user {user_id}: {e}")
            return False
