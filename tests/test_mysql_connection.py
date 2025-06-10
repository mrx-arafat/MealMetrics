#!/usr/bin/env python3
"""
Test MySQL connection for MealMetrics bot
"""

import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from database.factory import create_database_manager

def test_mysql_connection():
"""Test the MySQL database connection"""
print(" Testing MySQL Database Connection...")
print("=" * 50)

try:
# Load configuration
config = Config()
print(f" Database Type: {config.DATABASE_TYPE}")
print(f" MySQL Host: {config.MYSQL_HOST}")
print(f" MySQL Port: {config.MYSQL_PORT}")
print(f" MySQL User: {config.MYSQL_USER}")
print(f" MySQL Database: {config.MYSQL_DATABASE}")
print()

# Test connection with different methods
print(" Attempting to connect...")

# First, try a basic ping test
import socket
print(" Testing network connectivity...")
try:
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
result = sock.connect_ex((config.MYSQL_HOST, int(config.MYSQL_PORT)))
sock.close()
if result == 0:
print(" Network connection to MySQL server successful!")
else:
print(f" Network connection failed with error code: {result}")
return False
except Exception as e:
print(f" Network test failed: {e}")
return False

# Try direct MySQL connection
print(" Testing MySQL connection...")
try:
import mysql.connector
conn = mysql.connector.connect(
host=config.MYSQL_HOST,
port=config.MYSQL_PORT,
user=config.MYSQL_USER,
password=config.MYSQL_PASSWORD,
connect_timeout=10
)
print(" Direct MySQL connection successful!")
cursor = conn.cursor()

# Test query
cursor.execute("SELECT VERSION()")
version = cursor.fetchone()
print(f" MySQL Version: {version[0]}")

# Test database creation/selection
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DATABASE}")
cursor.execute(f"USE {config.MYSQL_DATABASE}")
print(f" Database '{config.MYSQL_DATABASE}' ready!")

cursor.close()
conn.close()

# Now test with database manager
print(" Testing database manager...")
db_manager = create_database_manager()
print(" Database manager created successfully!")

# Test table creation (this will be done by the database manager)
print(" Initializing tables...")
db_manager.init_database()
print(" All tables created successfully!")

# Test user creation
print(" Testing user operations...")
success = db_manager.create_user(
user_id=123456789,
username="test_user",
first_name="Test",
last_name="User"
)

if success:
print(" User creation test passed!")
else:
print(" User creation test failed!")

except mysql.connector.Error as e:
print(f" MySQL connection failed: {e}")
return False

print()
print(" All tests passed! Your MySQL database is ready for MealMetrics!")
print(" You can now run the bot with: python main.py")
return True

except Exception as e:
print(f" Connection failed: {e}")
print()
print(" Troubleshooting tips:")
print("1. Check if MySQL server is running")
print("2. Verify your credentials in .env file")
print("3. Ensure the database user has proper permissions")
print("4. Check if the host/port is accessible")
return False

if __name__ == "__main__":
success = test_mysql_connection()
sys.exit(0 if success else 1)
