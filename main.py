#!/usr/bin/env python3
"""
MealMetrics - AI-Powered Calorie Tracking Telegram Bot

A Telegram bot that analyzes food photos to estimate calories and track daily intake.
"""

import logging
import asyncio
import sys
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config import Config
from database.factory import create_database_manager
from bot.handlers import BotHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('mealmetrics.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class MealMetricsBot:
    """Main bot application class"""
    
    def __init__(self):
        self.config = Config()
        self.db_manager = None
        self.handlers = None
        self.application = None
    
    def initialize(self):
        """Initialize bot components"""
        try:
            # Validate configuration
            self.config.validate()
            logger.info("Configuration validated successfully")
            
            # Initialize database
            self.db_manager = create_database_manager()
            logger.info("Database initialized successfully")
            
            # Initialize handlers
            self.handlers = BotHandlers(self.db_manager)
            logger.info("Bot handlers initialized successfully")
            
            # Create application
            self.application = Application.builder().token(self.config.TELEGRAM_BOT_TOKEN).build()
            
            # Register handlers
            self._register_handlers()
            logger.info("Bot handlers registered successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            return False
    
    def _register_handlers(self):
        """Register all bot handlers"""
        app = self.application
        
        # Command handlers
        app.add_handler(CommandHandler("start", self.handlers.start_command))
        app.add_handler(CommandHandler("help", self.handlers.help_command))
        app.add_handler(CommandHandler("menu", self.handlers.menu_command))
        app.add_handler(CommandHandler("today", self.handlers.today_command))
        app.add_handler(CommandHandler("stats", self.handlers.stats_command))
        app.add_handler(CommandHandler("clear", self.handlers.clear_command))
        
        # Message handlers
        app.add_handler(MessageHandler(filters.PHOTO, self.handlers.handle_photo))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.handle_text))
        
        # Callback query handler
        app.add_handler(CallbackQueryHandler(self.handlers.handle_callback))
        
        # Error handler
        app.add_error_handler(self._error_handler)
    
    async def _error_handler(self, update: Update, context):
        """Enhanced error handler with detailed logging and user feedback"""
        error = context.error
        logger.error(f"Exception while handling an update: {error}", exc_info=True)

        # Log additional context for debugging
        if update:
            logger.error(f"Update that caused error: {update}")
            if update.effective_user:
                logger.error(f"User: {update.effective_user.id} (@{update.effective_user.username})")

        # Determine appropriate error message based on error type
        if "timeout" in str(error).lower():
            error_message = "⏱️ Request timed out. Please try again in a moment."
        elif "network" in str(error).lower() or "connection" in str(error).lower():
            error_message = "🌐 Network issue detected. Please check your connection and try again."
        elif "json" in str(error).lower():
            error_message = "🤖 AI response formatting issue. Please try again with a different photo."
        elif "rate limit" in str(error).lower():
            error_message = "⏳ Too many requests. Please wait a moment before trying again."
        else:
            error_message = "❌ Something went wrong. Please try again or use /help for assistance."

        # Try to send error message to user if possible
        if update and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_message,
                    parse_mode=None  # Use plain text for error messages to avoid formatting issues
                )
            except Exception as e:
                logger.error(f"Failed to send error message to user: {e}")
    
    async def start(self):
        """Start the bot"""
        if not self.initialize():
            logger.error("Failed to initialize bot. Exiting.")
            return False
        
        logger.info("Starting MealMetrics bot...")
        
        try:
            # Start the bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("MealMetrics bot is running!")
            logger.info("Press Ctrl+C to stop the bot")

            # Keep the bot running
            import signal
            import asyncio

            # Create a future that will be set when we receive a stop signal
            stop_event = asyncio.Event()

            def signal_handler(_signum, _frame):
                # Signal handler for graceful shutdown
                stop_event.set()

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Wait for stop signal
            await stop_event.wait()
            
        except KeyboardInterrupt:
            logger.info("Received stop signal")
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            return False
        finally:
            # Cleanup
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Bot stopped")
        
        return True
    
    def run(self):
        """Run the bot (synchronous wrapper)"""
        try:
            return asyncio.run(self.start())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            return True
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            return False

def main():
    """Main entry point"""
    print("🍽️ MealMetrics - AI-Powered Calorie Tracking Bot")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file based on .env.example")
        print("Make sure to add your Telegram bot token and OpenRouter API key")
        return False
    
    # Create and run bot
    bot = MealMetricsBot()
    success = bot.run()
    
    if success:
        print("✅ Bot finished successfully")
    else:
        print("❌ Bot finished with errors")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
