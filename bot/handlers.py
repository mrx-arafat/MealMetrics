import logging
import os
import tempfile
import asyncio
import random
from datetime import datetime, date, timedelta
from telegram import Update, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from PIL import Image

from utils.config import Config
from utils.helpers import validate_image_format, format_meal_summary, get_current_date, format_calories, format_timestamp_for_user
from database.models import DatabaseManager
from database.operations import MealOperations
from database.mysql_manager import MySQLDatabaseManager
from database.mysql_operations import MySQLMealOperations
from ai.vision_analyzer import VisionAnalyzer
from .keyboards import BotKeyboards
from .states import CallbackData

logger = logging.getLogger(__name__)

class BotHandlers:
    """Message and callback handlers for the MealMetrics bot"""

    # Dynamic food examples for tip messages
    FOOD_EXAMPLES = [
        "200g grilled chicken with rice",
        "Large pepperoni pizza slice",
        "Medium coffee with milk",
        "Fresh fruit salad bowl",
        "500ml mango juice without sugar",
        "Homemade pasta with tomato sauce",
        "Greek yogurt with honey and nuts",
        "Grilled salmon with vegetables",
        "Chocolate chip cookie (2 pieces)",
        "Green smoothie with spinach and banana",
        "Caesar salad with chicken",
        "Beef burger with fries",
        "Sushi roll (8 pieces)",
        "Oatmeal with berries and almonds",
        "Cheese sandwich on whole wheat"
    ]

    def __init__(self, db_manager):
        """Initialize handlers with database manager"""
        self.db = db_manager

        # Initialize appropriate operations class based on database type
        if isinstance(db_manager, MySQLDatabaseManager):
            self.meal_ops = MySQLMealOperations(db_manager)
        else:
            self.meal_ops = MealOperations(db_manager)

        self.vision_analyzer = VisionAnalyzer()
        self.keyboards = BotKeyboards()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Create or update user in database
        self.db.create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        welcome_message = (
            f"🍽️ Welcome to MealMetrics, {user.first_name}!\n\n"
            "I'm your personal calorie tracking assistant. Here's how I work:\n\n"
            "📸 **Send me a photo** of your meal\n"
            "💬 **Add a caption** with details (optional but recommended!)\n"
            "🤖 **I'll analyze it** and estimate calories\n"
            "✅ **Choose to log or cancel** the meal\n"
            "📊 **Track your daily intake** automatically\n\n"
            "💡 **Pro tip:** Add captions like '500ml mango juice without sugar' for super accurate results!\n\n"
            "Ready to start? Send me a photo of your meal! 📷"
        )
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=self.keyboards.main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "🤖 **MealMetrics Help**\n\n"
            "**How to use:**\n"
            "1. Take a clear photo of your meal\n"
            "2. Send the photo to me\n"
            "3. I'll analyze and estimate calories\n"
            "4. Choose to log the meal or cancel\n\n"
            "**Commands:**\n"
            "/start - Start the bot\n"
            "/help - Show this help\n"
            "/menu - Show main menu\n"
            "/today - Today's summary\n"
            "/stats - Weekly statistics\n\n"
            "**Tips for better accuracy:**\n"
            "• Take photos in good lighting\n"
            "• Include the entire meal in frame\n"
            "• Avoid blurry or dark photos\n"
            "• Use standard plates/bowls when possible\n"
            "• Add captions with details like '500ml mango juice without sugar'\n"
            "• Mention quantities, brands, or preparation methods"
        )
        
        await update.message.reply_text(
            help_message,
            reply_markup=self.keyboards.help_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /menu command"""
        menu_message = (
            "🏠 **Main Menu**\n\n"
            "📋 **Choose an option below:**"
        )

        await update.message.reply_text(
            menu_message,
            reply_markup=self.keyboards.main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /today command"""
        user_id = update.effective_user.id
        self.db.update_user_activity(user_id)

        # Get user's timezone offset from Telegram (if available)
        user_timezone_offset = None
        if hasattr(update.effective_user, 'timezone_offset'):
            user_timezone_offset = update.effective_user.timezone_offset

        meals_today = self.meal_ops.get_user_meals_today(user_id)
        summary = format_meal_summary(meals_today, user_timezone_offset)

        await update.message.reply_text(
            summary,
            reply_markup=self.keyboards.back_to_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        await update.message.reply_text(
            "📊 **Statistics**\n\nChoose a time period:",
            reply_markup=self.keyboards.stats_options(),
            parse_mode=ParseMode.MARKDOWN
        )

    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        await update.message.reply_text(
            "🗑️ **Data Management**\n\nChoose an option:",
            reply_markup=self.keyboards.data_management(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages with optional captions"""
        user_id = update.effective_user.id
        self.db.update_user_activity(user_id)

        # Get caption if provided
        caption = update.message.caption if update.message.caption else None

        # Send processing message with caption acknowledgment or tip
        if caption:
            # User provided caption - analyze directly
            processing_msg = await update.message.reply_text(
                f"🔍 Analyzing your meal with details: *{caption}*\n\nThis may take a moment...",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # No caption - show tip with dynamic example for 3 seconds
            random_example = random.choice(self.FOOD_EXAMPLES)
            tip_msg = await update.message.reply_text(
                f"🔍 Analyzing your meal...\n\n💡 *Tip: Add a caption with details like '{random_example}' for more accurate results!*",
                parse_mode=ParseMode.MARKDOWN
            )

            # Wait for 3 seconds
            await asyncio.sleep(3)

            # Update message to show analysis in progress
            processing_msg = await tip_msg.edit_text(
                "🔍 Analyzing your meal... This may take a moment.\n\n💡 *Getting detailed nutritional breakdown...*",
                parse_mode=ParseMode.MARKDOWN
            )
        
        try:
            # Get the largest photo
            photo = update.message.photo[-1]
            
            # Download photo
            photo_file = await photo.get_file()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                await photo_file.download_to_drive(temp_file.name)
                temp_path = temp_file.name
            
            try:
                # Open and process image
                with Image.open(temp_path) as image:
                    # Convert to RGB if necessary
                    if image.mode != 'RGB':
                        image = image.convert('RGB')

                    # Analyze the image with caption context
                    analysis_result, error = self.vision_analyzer.analyze_food_image(image, caption)
                
                # Clean up temp file
                os.unlink(temp_path)
                
                if error:
                    # Provide more specific error messages based on error type
                    if "timeout" in error.lower():
                        error_message = (
                            "⏱️ **Analysis Timeout**\n\n"
                            "The AI service took too long to respond. This can happen during high traffic.\n\n"
                            "**Please try again in a moment.**"
                        )
                    elif "network" in error.lower() or "connection" in error.lower():
                        error_message = (
                            "🌐 **Connection Issue**\n\n"
                            "There's a temporary network issue connecting to the AI service.\n\n"
                            "**Please check your connection and try again.**"
                        )
                    elif "json" in error.lower() or "parse" in error.lower():
                        error_message = (
                            "🤖 **AI Response Issue**\n\n"
                            "The AI had trouble processing your image. This sometimes happens with complex photos.\n\n"
                            "**Try taking a clearer photo with better lighting.**"
                        )
                    else:
                        error_message = (
                            "❌ **Analysis Failed**\n\n"
                            "I couldn't analyze your meal due to a technical issue.\n\n"
                            "**Please try again with a different photo.**"
                        )

                    await processing_msg.edit_text(
                        error_message,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    return

                if not analysis_result:
                    await processing_msg.edit_text(
                        "❌ **Analysis Failed**\n\n"
                        "I couldn't identify any food in your photo.\n\n"
                        "**Tips for better results:**\n"
                        "• Take photos in good lighting\n"
                        "• Make sure food is clearly visible\n"
                        "• Avoid blurry or dark images\n"
                        "• Include the entire meal in frame",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    return
                
                # Store pending meal
                meal_id = self.db.add_pending_meal(
                    user_id=user_id,
                    description=analysis_result['description'],
                    calories=analysis_result['total_calories'],
                    confidence=analysis_result['confidence']
                )
                
                if not meal_id:
                    await processing_msg.edit_text(
                        "❌ Sorry, there was an error processing your meal. Please try again.",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    return
                
                # Format and send analysis with error handling
                try:
                    analysis_text = self.vision_analyzer.format_analysis_for_user(analysis_result)

                    await processing_msg.edit_text(
                        analysis_text,
                        reply_markup=self.keyboards.meal_confirmation(meal_id),
                        parse_mode=ParseMode.MARKDOWN
                    )
                except Exception as format_error:
                    logger.warning(f"Markdown formatting failed, using plain text: {format_error}")

                    # Fallback to plain text without markdown
                    description = analysis_result.get('description', 'Food item')
                    calories = analysis_result.get('total_calories', 0)
                    confidence = analysis_result.get('confidence', 70)

                    fallback_text = (
                        f"🍽️ {description}\n\n"
                        f"🔥 Calories: {calories:.0f}\n"
                        f"📊 Confidence: {confidence:.0f}%\n\n"
                        f"Ready to log this meal?"
                    )

                    await processing_msg.edit_text(
                        fallback_text,
                        reply_markup=self.keyboards.meal_confirmation(meal_id),
                        parse_mode=None  # No markdown parsing
                    )
                
            finally:
                # Always clean up temp file
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                        logger.debug(f"Cleaned up temp file: {temp_path}")
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to cleanup temp file {temp_path}: {cleanup_error}")
                
        except Exception as e:
            logger.error(f"Error processing photo for user {user_id}: {e}")

            # Provide helpful error message based on error type
            if "Can't parse entities" in str(e):
                error_message = (
                    "🤖 **Processing Complete**\n\n"
                    "I analyzed your meal but had trouble formatting the response.\n\n"
                    "**Please try sending the photo again for a properly formatted result.**"
                )
            elif "timeout" in str(e).lower():
                error_message = (
                    "⏱️ **Request Timeout**\n\n"
                    "The analysis took too long to complete.\n\n"
                    "**Please try again in a moment.**"
                )
            else:
                error_message = (
                    "❌ **Processing Error**\n\n"
                    "There was an unexpected error analyzing your photo.\n\n"
                    "**Please try again with a different photo.**"
                )

            try:
                await processing_msg.edit_text(
                    error_message,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception:
                # Final fallback - plain text without any formatting
                await processing_msg.edit_text(
                    "Sorry, there was an error processing your photo. Please try again.",
                    parse_mode=None
                )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        self.db.update_user_activity(user_id)
        
        text = update.message.text.lower()
        
        if any(word in text for word in ['hi', 'hello', 'hey', 'start']):
            await self.start_command(update, context)
        elif any(word in text for word in ['help', 'how', 'what']):
            await self.help_command(update, context)
        elif any(word in text for word in ['menu', 'options']):
            await self.menu_command(update, context)
        elif any(word in text for word in ['today', 'summary']):
            await self.today_command(update, context)
        elif any(word in text for word in ['stats', 'statistics']):
            await self.stats_command(update, context)
        else:
            await update.message.reply_text(
                "📸 Please send me a photo of your meal to get started!\n\n"
                "Or use /help to see what I can do.",
                reply_markup=self.keyboards.main_menu(),
                parse_mode=ParseMode.MARKDOWN
            )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        user_id = query.from_user.id
        self.db.update_user_activity(user_id)

        await query.answer()  # Acknowledge the callback

        action, params = CallbackData.parse_callback(query.data)

        try:
            if action == CallbackData.LOG_MEAL:
                await self._handle_log_meal(query, params[0] if params else None)
            elif action == CallbackData.CANCEL_MEAL:
                await self._handle_cancel_meal(query, params[0] if params else None)
            elif action == CallbackData.MAIN_MENU:
                await self._handle_main_menu(query)
            elif action == CallbackData.TODAY_SUMMARY:
                await self._handle_today_summary(query)
            elif action == CallbackData.WEEKLY_STATS:
                await self._handle_weekly_stats(query)
            elif action == CallbackData.VIEW_HISTORY:
                await self._handle_view_history(query)
            elif action == CallbackData.HISTORY_PREV:
                date_str = params[0] if params else get_current_date()
                # Calculate previous date
                try:
                    from datetime import datetime, timedelta
                    current_date = datetime.fromisoformat(date_str)
                    prev_date = (current_date - timedelta(days=1)).date().isoformat()
                    await self._handle_view_history(query, prev_date)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing date for history navigation: {e}")
                    await self._handle_view_history(query)
            elif action == CallbackData.HISTORY_NEXT:
                date_str = params[0] if params else get_current_date()
                # Calculate next date
                try:
                    from datetime import datetime, timedelta
                    current_date = datetime.fromisoformat(date_str)
                    next_date = (current_date + timedelta(days=1)).date().isoformat()
                    await self._handle_view_history(query, next_date)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing date for history navigation: {e}")
                    await self._handle_view_history(query)
            elif action == CallbackData.HELP:
                await self._handle_help(query)
            elif action == CallbackData.MANAGE_DATA:
                await self._handle_manage_data(query)
            elif action == CallbackData.DATA_SUMMARY:
                await self._handle_data_summary(query)
            elif action == CallbackData.CLEAR_TODAY:
                await self._handle_clear_today_confirm(query)
            elif action == CallbackData.CLEAR_ALL_CONFIRM:
                await self._handle_clear_all_confirm(query)
            elif action == CallbackData.CONFIRM_CLEAR_TODAY:
                await self._handle_confirm_clear_today(query)
            elif action == CallbackData.CONFIRM_CLEAR_ALL:
                await self._handle_confirm_clear_all(query)
            elif action.startswith("help_"):
                await self._handle_help_section(query, action)
            elif action.startswith("stats_"):
                await self._handle_stats_section(query, action)
            else:
                await query.edit_message_text(
                    "❌ Unknown action. Please try again.",
                    reply_markup=self.keyboards.main_menu()
                )
        except Exception as e:
            logger.error(f"Error handling callback {query.data} for user {user_id}: {e}")
            await query.edit_message_text(
                "❌ An error occurred. Please try again.",
                reply_markup=self.keyboards.main_menu()
            )

    async def _handle_log_meal(self, query, meal_id_str):
        """Handle meal logging confirmation"""
        if not meal_id_str:
            await query.edit_message_text(
                "❌ Invalid meal ID. Please try again.",
                reply_markup=self.keyboards.main_menu()
            )
            return

        try:
            meal_id = int(meal_id_str)
            user_id = query.from_user.id

            # Get pending meal
            pending_meal = self.db.get_pending_meal(user_id, meal_id)
            if not pending_meal:
                await query.edit_message_text(
                    "❌ Meal not found or already processed.",
                    reply_markup=self.keyboards.main_menu()
                )
                return

            # Log the meal
            success = self.meal_ops.log_meal(
                user_id=user_id,
                description=pending_meal['description'],
                calories=pending_meal['calories'],
                confidence=pending_meal['confidence']
            )

            if success:
                # Delete pending meal
                self.db.delete_pending_meal(user_id, meal_id)

                # Get updated daily summary
                meals_today = self.meal_ops.get_user_meals_today(user_id)
                total_today = sum(meal['calories'] for meal in meals_today)

                # Remove the Log/Cancel buttons from the original analysis message
                await query.edit_message_reply_markup(reply_markup=None)

                # Send a NEW confirmation message (don't replace the analysis)
                confirmation_message = (
                    f"✅ **Meal logged successfully!**\n\n"
                    f"🍽️ {pending_meal['description']}\n"
                    f"🔥 {format_calories(pending_meal['calories'])}\n\n"
                    f"📊 **Today's total:** {format_calories(total_today)}\n"
                    f"📝 **Meals logged today:** {len(meals_today)}\n\n"
                    f"⏳ *This message will update in 3 seconds...*"
                )

                # Send new message instead of editing the analysis
                confirmation_msg = await query.message.reply_text(
                    confirmation_message,
                    parse_mode=ParseMode.MARKDOWN
                )

                # Wait for 3 seconds
                await asyncio.sleep(3)

                # Update the confirmation message with final state
                final_message = (
                    f"✅ **Meal logged successfully!**\n\n"
                    f"🍽️ {pending_meal['description']}\n"
                    f"🔥 {format_calories(pending_meal['calories'])}\n\n"
                    f"📊 **Today's total:** {format_calories(total_today)}\n"
                    f"📝 **Meals logged today:** {len(meals_today)}\n\n"
                    f"📸 *Ready to track another meal? Send me a photo!*"
                )

                await confirmation_msg.edit_text(
                    final_message,
                    reply_markup=self.keyboards.main_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.edit_message_text(
                    "❌ Failed to log meal. Please try again.",
                    reply_markup=self.keyboards.main_menu()
                )

        except ValueError:
            await query.edit_message_text(
                "❌ Invalid meal ID format.",
                reply_markup=self.keyboards.main_menu()
            )

    async def _handle_cancel_meal(self, query, meal_id_str):
        """Handle meal cancellation"""
        if not meal_id_str:
            await query.edit_message_text(
                "❌ Invalid meal ID.",
                reply_markup=self.keyboards.main_menu()
            )
            return

        try:
            meal_id = int(meal_id_str)
            user_id = query.from_user.id

            # Delete pending meal
            success = self.db.delete_pending_meal(user_id, meal_id)

            if success:
                # Remove the Log/Cancel buttons from the original analysis message
                await query.edit_message_reply_markup(reply_markup=None)

                # Send a NEW cancellation message (don't replace the analysis)
                cancellation_message = (
                    f"❌ **Meal not logged**\n\n"
                    f"The meal analysis has been cancelled and won't be added to your daily intake.\n\n"
                    f"⏳ *This message will update in 3 seconds...*"
                )

                # Send new message instead of editing the analysis
                cancellation_msg = await query.message.reply_text(
                    cancellation_message,
                    parse_mode=ParseMode.MARKDOWN
                )

                # Wait for 3 seconds
                await asyncio.sleep(3)

                # Update the cancellation message with final state
                final_message = (
                    f"❌ **Meal not logged**\n\n"
                    f"No worries! The meal analysis has been cancelled.\n\n"
                    f"📸 *Ready to track a meal? Send me a photo!*"
                )

                await cancellation_msg.edit_text(
                    final_message,
                    reply_markup=self.keyboards.main_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.edit_message_text(
                    "❌ Meal not found or already processed.",
                    reply_markup=self.keyboards.main_menu()
                )

        except ValueError:
            await query.edit_message_text(
                "❌ Invalid meal ID format.",
                reply_markup=self.keyboards.main_menu()
            )

    async def _handle_main_menu(self, query):
        """Handle main menu display"""
        menu_message = (
            "🏠 **Main Menu**\n\n"
            "📋 **Choose an option below:**"
        )

        await query.edit_message_text(
            menu_message,
            reply_markup=self.keyboards.main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

    async def _handle_today_summary(self, query):
        """Handle today's summary display"""
        user_id = query.from_user.id

        # Get user's timezone offset from Telegram (if available)
        user_timezone_offset = None
        if hasattr(query.from_user, 'timezone_offset'):
            user_timezone_offset = query.from_user.timezone_offset

        meals_today = self.meal_ops.get_user_meals_today(user_id)
        summary = format_meal_summary(meals_today, user_timezone_offset)

        await query.edit_message_text(
            summary,
            reply_markup=self.keyboards.back_to_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

    async def _handle_weekly_stats(self, query):
        """Handle weekly statistics display"""
        user_id = query.from_user.id
        stats = self.meal_ops.get_user_stats(user_id, days=7)

        if not stats or stats.get('days_tracked', 0) == 0:
            message = "📊 **Weekly Statistics**\n\nNo meals logged in the past 7 days.\nStart tracking by sending me a photo of your meal!"
        else:
            message = (
                f"📊 **Weekly Statistics (Last 7 Days)**\n\n"
                f"🔥 **Total Calories:** {format_calories(stats['total_calories'])}\n"
                f"🍽️ **Total Meals:** {stats['total_meals']}\n"
                f"📅 **Days Tracked:** {stats['days_tracked']}/7\n"
                f"📈 **Avg Calories/Day:** {format_calories(stats['avg_calories_per_day'])}\n"
                f"🍽️ **Avg Meals/Day:** {stats['avg_meals_per_day']:.1f}"
            )

        await query.edit_message_text(
            message,
            reply_markup=self.keyboards.back_to_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

    async def _handle_view_history(self, query, date_str: str = None):
        """Handle meal history viewing with date navigation"""
        user_id = query.from_user.id

        # If no date specified, start with today
        if not date_str:
            date_str = get_current_date()

        # Get user's timezone offset from Telegram (if available)
        user_timezone_offset = None
        if hasattr(query.from_user, 'timezone_offset'):
            user_timezone_offset = query.from_user.timezone_offset

        # Get meals for the specified date
        meals = self.meal_ops.get_user_meals_by_date(user_id, date_str)

        # Format the date for display
        try:
            from datetime import datetime
            date_obj = datetime.fromisoformat(date_str)
            formatted_date = date_obj.strftime("%B %d, %Y")  # e.g., "January 15, 2024"
        except (ValueError, TypeError) as e:
            logger.warning(f"Error formatting date {date_str}: {e}")
            formatted_date = date_str

        # Create history message
        if not meals:
            message = (
                f"📅 **Meal History - {formatted_date}**\n\n"
                f"🍽️ No meals logged on this date.\n\n"
                f"Use the navigation buttons to browse other dates."
            )
        else:
            total_calories = sum(meal['calories'] for meal in meals)
            meal_count = len(meals)

            message = (
                f"📅 **Meal History - {formatted_date}**\n\n"
                f"🍽️ **Meals logged:** {meal_count}\n"
                f"🔥 **Total calories:** {format_calories(total_calories)}\n\n"
            )

            if meal_count > 0:
                message += "**Meals:**\n"
                for i, meal in enumerate(meals, 1):
                    try:
                        # Use the timezone-aware formatting function
                        time_str = format_timestamp_for_user(meal['timestamp'], user_timezone_offset)

                        # Truncate description and escape markdown
                        description = meal['description'][:50] + "..." if len(meal['description']) > 50 else meal['description']
                        description = description.replace('*', '\\*').replace('_', '\\_')

                        message += f"{i}. {description} - {format_calories(meal['calories'])} ({time_str})\n"
                    except Exception as e:
                        logger.warning(f"Error formatting meal {i}: {e}")
                        continue

        # Determine navigation availability
        from datetime import datetime, timedelta
        try:
            current_date = datetime.fromisoformat(date_str)
            today = datetime.now().date()

            # Can go to previous day (no limit on past)
            has_prev = True

            # Can go to next day only if not today or future
            has_next = current_date.date() < today

            prev_date = (current_date - timedelta(days=1)).date().isoformat()
            next_date = (current_date + timedelta(days=1)).date().isoformat()

        except (ValueError, TypeError) as e:
            logger.warning(f"Error calculating navigation dates for {date_str}: {e}")
            has_prev = False
            has_next = False
            prev_date = None
            next_date = None

        # Create navigation keyboard
        keyboard = []

        # Navigation row
        nav_row = []
        if has_prev and prev_date:
            nav_row.append(InlineKeyboardButton("⬅️ Previous Day", callback_data=f"history_prev:{date_str}"))
        if has_next and next_date:
            nav_row.append(InlineKeyboardButton("➡️ Next Day", callback_data=f"history_next:{date_str}"))

        if nav_row:
            keyboard.append(nav_row)

        # Action row
        keyboard.append([
            InlineKeyboardButton("📊 Today's Summary", callback_data="today_summary"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

    async def _handle_help(self, query):
        """Handle help menu display"""
        help_message = (
            "🤖 **MealMetrics Help**\n\n"
            "**How to use:**\n"
            "1. Take a clear photo of your meal\n"
            "2. Send the photo to me\n"
            "3. I'll analyze and estimate calories\n"
            "4. Choose to log the meal or cancel\n\n"
            "**Tips for better accuracy:**\n"
            "• Take photos in good lighting\n"
            "• Include the entire meal in frame\n"
            "• Avoid blurry or dark photos\n"
            "• Use standard plates/bowls when possible"
        )

        await query.edit_message_text(
            help_message,
            reply_markup=self.keyboards.help_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

    async def _handle_help_section(self, query, action):
        """Handle specific help sections"""
        if action == "help_usage":
            message = (
                "📸 **How to Use MealMetrics**\n\n"
                "1. **Take a photo** of your meal\n"
                "   • Make sure the food is clearly visible\n"
                "   • Include the entire meal in the frame\n"
                "   • Use good lighting\n\n"
                "2. **Send the photo** to me\n"
                "   • I'll analyze it using AI\n"
                "   • This usually takes 5-10 seconds\n\n"
                "3. **Review the analysis**\n"
                "   • Check the calorie estimate\n"
                "   • Read the food breakdown\n\n"
                "4. **Choose an action**\n"
                "   • ✅ Log Meal - Add to your daily log\n"
                "   • ❌ Cancel - Discard the analysis"
            )
        elif action == "help_troubleshoot":
            message = (
                "🔧 **Troubleshooting**\n\n"
                "**If analysis fails:**\n"
                "• Check your internet connection\n"
                "• Try a clearer photo\n"
                "• Make sure the image isn't too large\n"
                "• Restart the bot with /start\n\n"
                "**For better accuracy:**\n"
                "• Use natural lighting\n"
                "• Avoid shadows on food\n"
                "• Include reference objects (plates, utensils)\n"
                "• Take photos from above when possible"
            )
        elif action == "help_accuracy":
            message = (
                "📊 **About Accuracy**\n\n"
                "**How it works:**\n"
                "• AI analyzes your food photos\n"
                "• Estimates portion sizes and ingredients\n"
                "• Calculates calories based on nutritional data\n\n"
                "**Accuracy factors:**\n"
                "• Photo quality and lighting\n"
                "• Visibility of all food items\n"
                "• Cooking methods and ingredients\n"
                "• Portion size estimation\n\n"
                "**Tips:**\n"
                "• Results are estimates, not exact measurements\n"
                "• Use for general tracking and trends\n"
                "• Consider logging cooking oils and sauces separately"
            )
        else:
            message = "❌ Unknown help section."

        await query.edit_message_text(
            message,
            reply_markup=self.keyboards.back_to_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

    async def _handle_stats_section(self, query, action):
        """Handle specific statistics sections"""
        user_id = query.from_user.id

        if action == "stats_today":
            await self._handle_today_summary(query)
        elif action == "stats_week":
            await self._handle_weekly_stats(query)
        elif action == "stats_month":
            stats = self.meal_ops.get_user_stats(user_id, days=30)

            if not stats or stats.get('days_tracked', 0) == 0:
                message = "📊 **Monthly Statistics**\n\nNo meals logged in the past 30 days.\nStart tracking by sending me a photo of your meal!"
            else:
                message = (
                    f"📊 **Monthly Statistics (Last 30 Days)**\n\n"
                    f"🔥 **Total Calories:** {format_calories(stats['total_calories'])}\n"
                    f"🍽️ **Total Meals:** {stats['total_meals']}\n"
                    f"📅 **Days Tracked:** {stats['days_tracked']}/30\n"
                    f"📈 **Avg Calories/Day:** {format_calories(stats['avg_calories_per_day'])}\n"
                    f"🍽️ **Avg Meals/Day:** {stats['avg_meals_per_day']:.1f}"
                )

            await query.edit_message_text(
                message,
                reply_markup=self.keyboards.back_to_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                "❌ Unknown statistics section.",
                reply_markup=self.keyboards.back_to_menu()
            )

    async def _handle_manage_data(self, query):
        """Handle data management menu"""
        await query.edit_message_text(
            "🗑️ **Data Management**\n\nChoose an option:",
            reply_markup=self.keyboards.data_management(),
            parse_mode=ParseMode.MARKDOWN
        )

    async def _handle_data_summary(self, query):
        """Handle data summary display"""
        user_id = query.from_user.id
        summary = self.meal_ops.get_user_data_summary(user_id)

        if not summary or summary.get('total_meals', 0) == 0:
            message = "📋 **Data Summary**\n\nNo meal data found.\nStart tracking by sending me a photo of your meal!"
        else:
            message = (
                f"📋 **Data Summary**\n\n"
                f"🍽️ **Total Meals:** {summary['total_meals']}\n"
                f"📅 **Days with Data:** {summary['days_with_data']}\n"
                f"🔥 **Total Calories:** {format_calories(summary['total_calories'])}\n\n"
            )

            if summary['first_meal_date'] and summary['last_meal_date']:
                message += f"📆 **Date Range:** {summary['first_meal_date']} to {summary['last_meal_date']}\n"

            if summary['days_with_data'] > 0:
                avg_calories = summary['total_calories'] / summary['days_with_data']
                avg_meals = summary['total_meals'] / summary['days_with_data']
                message += f"📊 **Daily Average:** {format_calories(avg_calories)} ({avg_meals:.1f} meals/day)"

        await query.edit_message_text(
            message,
            reply_markup=self.keyboards.data_management(),
            parse_mode=ParseMode.MARKDOWN
        )

    async def _handle_clear_today_confirm(self, query):
        """Handle clear today confirmation"""
        today = get_current_date()
        message = (
            f"⚠️ **Clear Today's Data**\n\n"
            f"Are you sure you want to delete all meals logged for {today}?\n\n"
            f"This action cannot be undone!"
        )

        await query.edit_message_text(
            message,
            reply_markup=self.keyboards.clear_confirmation("clear_today"),
            parse_mode=ParseMode.MARKDOWN
        )

    async def _handle_clear_all_confirm(self, query):
        """Handle clear all data confirmation"""
        user_id = query.from_user.id
        summary = self.meal_ops.get_user_data_summary(user_id)

        message = (
            f"🚨 **Clear ALL Data**\n\n"
            f"Are you sure you want to delete ALL your meal data?\n\n"
            f"This will remove:\n"
            f"• {summary.get('total_meals', 0)} meals\n"
            f"• {summary.get('days_with_data', 0)} days of data\n"
            f"• All statistics and history\n\n"
            f"⚠️ **This action cannot be undone!**"
        )

        await query.edit_message_text(
            message,
            reply_markup=self.keyboards.clear_confirmation("clear_all"),
            parse_mode=ParseMode.MARKDOWN
        )

    async def _handle_confirm_clear_today(self, query):
        """Handle confirmed clear today action"""
        user_id = query.from_user.id
        today = get_current_date()

        success = self.meal_ops.clear_user_data_by_date(user_id, today)

        if success:
            message = f"✅ **Data Cleared**\n\nAll meals for {today} have been deleted."
        else:
            message = f"❌ **Error**\n\nFailed to clear data for {today}. Please try again."

        await query.edit_message_text(
            message,
            reply_markup=self.keyboards.data_management(),
            parse_mode=ParseMode.MARKDOWN
        )

    async def _handle_confirm_clear_all(self, query):
        """Handle confirmed clear all data action"""
        user_id = query.from_user.id

        success = self.meal_ops.clear_all_user_data(user_id)

        if success:
            message = "✅ **All Data Cleared**\n\nAll your meal data has been permanently deleted."
        else:
            message = "❌ **Error**\n\nFailed to clear all data. Please try again."

        await query.edit_message_text(
            message,
            reply_markup=self.keyboards.main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
