import mysql.connector
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import logging
from utils.config import Config

logger = logging.getLogger(__name__)

class MySQLDatabaseManager:
    """MySQL database manager for MealMetrics bot"""

    def __init__(self):
        self.config = Config()
        self.connection_config = {
            'host': self.config.MYSQL_HOST,
            'port': self.config.MYSQL_PORT,
            'user': self.config.MYSQL_USER,
            'password': self.config.MYSQL_PASSWORD,
            'database': self.config.MYSQL_DATABASE,
            'autocommit': True
        }
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = mysql.connector.connect(**self.connection_config)
            return conn
        except mysql.connector.Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    created_at DATETIME NOT NULL,
                    last_active DATETIME NOT NULL
                )
            ''')
            
            # Meals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    description TEXT NOT NULL,
                    calories DECIMAL(8,2) NOT NULL,
                    confidence DECIMAL(5,2),
                    image_path TEXT,
                    timestamp DATETIME NOT NULL,
                    date DATE NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Daily summaries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_summaries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    date DATE NOT NULL,
                    total_calories DECIMAL(8,2) NOT NULL,
                    meal_count INT NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    UNIQUE KEY unique_user_date (user_id, date),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Pending meals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pending_meals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    description TEXT NOT NULL,
                    calories DECIMAL(8,2) NOT NULL,
                    confidence DECIMAL(5,2),
                    image_path TEXT,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            cursor.close()
            conn.close()
            logger.info("MySQL database initialized successfully")
            
        except mysql.connector.Error as e:
            logger.error(f"Error initializing MySQL database: {e}")
            raise
    
    def create_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> bool:
        """Create or update user in database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            now = datetime.now()
            
            # Check if user exists
            cursor.execute('SELECT created_at FROM users WHERE user_id = %s', (user_id,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Update existing user
                cursor.execute('''
                    UPDATE users 
                    SET username = %s, first_name = %s, last_name = %s, last_active = %s
                    WHERE user_id = %s
                ''', (username, first_name, last_name, now, user_id))
            else:
                # Create new user
                cursor.execute('''
                    INSERT INTO users 
                    (user_id, username, first_name, last_name, created_at, last_active)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (user_id, username, first_name, last_name, now, now))
            
            cursor.close()
            conn.close()
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"Error creating/updating user {user_id}: {e}")
            return False
    
    def update_user_activity(self, user_id: int) -> bool:
        """Update user's last activity timestamp"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET last_active = %s WHERE user_id = %s',
                (datetime.now(), user_id)
            )
            cursor.close()
            conn.close()
            return True
        except mysql.connector.Error as e:
            logger.error(f"Error updating user activity for {user_id}: {e}")
            return False
    
    def add_pending_meal(self, user_id: int, description: str, calories: float, 
                        confidence: float = None, image_path: str = None) -> Optional[int]:
        """Add a pending meal (waiting for user confirmation)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pending_meals 
                (user_id, description, calories, confidence, image_path, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, description, calories, confidence, image_path, datetime.now()))
            
            meal_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return meal_id
        except mysql.connector.Error as e:
            logger.error(f"Error adding pending meal for user {user_id}: {e}")
            return None
    
    def get_pending_meal(self, user_id: int, meal_id: int) -> Optional[Dict[str, Any]]:
        """Get a pending meal by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                'SELECT * FROM pending_meals WHERE user_id = %s AND id = %s',
                (user_id, meal_id)
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return row
        except mysql.connector.Error as e:
            logger.error(f"Error getting pending meal {meal_id} for user {user_id}: {e}")
            return None
    
    def delete_pending_meal(self, user_id: int, meal_id: int) -> bool:
        """Delete a pending meal"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM pending_meals WHERE user_id = %s AND id = %s',
                (user_id, meal_id)
            )
            affected_rows = cursor.rowcount
            cursor.close()
            conn.close()
            return affected_rows > 0
        except mysql.connector.Error as e:
            logger.error(f"Error deleting pending meal {meal_id} for user {user_id}: {e}")
            return False
