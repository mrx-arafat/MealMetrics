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
        """Validate that all required configuration is present and valid"""
        import logging
        logger = logging.getLogger(__name__)

        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'OPENROUTER_API_KEY'
        ]

        missing_vars = []
        invalid_vars = []

        for var in required_vars:
            value = getattr(cls, var)
            if not value:
                missing_vars.append(var)
            elif var == 'TELEGRAM_BOT_TOKEN' and not value.startswith(('bot', 'BOT')):
                # Basic validation for Telegram bot token format
                if ':' not in value or len(value) < 40:
                    invalid_vars.append(f"{var} (invalid format)")
            elif var == 'OPENROUTER_API_KEY' and len(value) < 10:
                invalid_vars.append(f"{var} (too short)")

        # Validate database configuration if using MySQL
        if cls.DATABASE_TYPE == 'mysql':
            mysql_vars = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_DATABASE']
            for var in mysql_vars:
                if not getattr(cls, var):
                    missing_vars.append(var)

        # Validate numeric configurations
        try:
            if cls.MAX_IMAGE_SIZE_MB <= 0:
                invalid_vars.append("MAX_IMAGE_SIZE_MB (must be positive)")
        except (ValueError, TypeError):
            invalid_vars.append("MAX_IMAGE_SIZE_MB (must be a number)")

        # Validate supported formats
        if not cls.SUPPORTED_IMAGE_FORMATS or not isinstance(cls.SUPPORTED_IMAGE_FORMATS, list):
            invalid_vars.append("SUPPORTED_IMAGE_FORMATS (must be a non-empty list)")

        # Report errors
        errors = []
        if missing_vars:
            errors.append(f"Missing required environment variables: {', '.join(missing_vars)}")
        if invalid_vars:
            errors.append(f"Invalid configuration values: {', '.join(invalid_vars)}")

        if errors:
            error_msg = "; ".join(errors)
            logger.error(f"Configuration validation failed: {error_msg}")
            raise ValueError(error_msg)

        logger.info("Configuration validation successful")
        return True
