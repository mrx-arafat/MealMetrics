"""
Database factory to create appropriate database manager based on configuration
"""
import logging
from utils.config import Config
from .models import DatabaseManager
from .mysql_manager import MySQLDatabaseManager

logger = logging.getLogger(__name__)

def create_database_manager():
    """Create appropriate database manager based on configuration"""
    config = Config()
    
    if config.DATABASE_TYPE.lower() == 'mysql':
        logger.info("Using MySQL database")
        return MySQLDatabaseManager()
    else:
        logger.info("Using SQLite database")
        return DatabaseManager(config.DATABASE_PATH)
