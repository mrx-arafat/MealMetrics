import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for MealMetrics bot"""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # OpenRouter API Configuration
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.5-flash-preview:thinking')
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # Database Configuration
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')  # 'sqlite' or 'mysql'
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'mealmetrics.db')  # For SQLite

    # MySQL Configuration (for production)
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'mealmetrics')

    # SSH Tunnel Configuration
    SSH_HOST = os.getenv('SSH_HOST', '')
    SSH_USER = os.getenv('SSH_USER', '')
    SSH_PASSWORD = os.getenv('SSH_PASSWORD', '')
    
    # Bot Configuration
    MAX_IMAGE_SIZE_MB = int(os.getenv('MAX_IMAGE_SIZE_MB', 10))
    SUPPORTED_IMAGE_FORMATS = os.getenv('SUPPORTED_IMAGE_FORMATS', 'jpg,jpeg,png,webp').split(',')
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'OPENROUTER_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
