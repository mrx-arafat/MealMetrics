from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Optional

class BotKeyboards:
    """Inline keyboards for the MealMetrics bot"""
    
    @staticmethod
    def meal_confirmation(meal_id: int) -> InlineKeyboardMarkup:
        """Keyboard for confirming or canceling a meal log"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Log Meal", callback_data=f"log_meal:{meal_id}"),
                InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_meal:{meal_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu keyboard with improved layout"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Today's Summary", callback_data="today_summary")
            ],
            [
                InlineKeyboardButton("📈 Weekly Stats", callback_data="weekly_stats"),
                InlineKeyboardButton("📅 View History", callback_data="view_history")
            ],
            [
                InlineKeyboardButton("🗑️ Manage Data", callback_data="manage_data"),
                InlineKeyboardButton("ℹ️ Help", callback_data="help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def history_navigation(current_date: str, has_prev: bool = True, has_next: bool = True) -> InlineKeyboardMarkup:
        """Navigation keyboard for viewing meal history"""
        keyboard = []
        
        # Navigation row
        nav_row = []
        if has_prev:
            nav_row.append(InlineKeyboardButton("⬅️ Previous Day", callback_data=f"history_prev:{current_date}"))
        if has_next:
            nav_row.append(InlineKeyboardButton("➡️ Next Day", callback_data=f"history_next:{current_date}"))
        
        if nav_row:
            keyboard.append(nav_row)
        
        # Action row
        keyboard.append([
            InlineKeyboardButton("📊 Today's Summary", callback_data="today_summary"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """Simple back to menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """Help menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📸 How to Use", callback_data="help_usage"),
                InlineKeyboardButton("🔧 Troubleshooting", callback_data="help_troubleshoot")
            ],
            [
                InlineKeyboardButton("📊 About Accuracy", callback_data="help_accuracy"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def stats_options() -> InlineKeyboardMarkup:
        """Statistics viewing options"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Today", callback_data="stats_today"),
                InlineKeyboardButton("📈 This Week", callback_data="stats_week")
            ],
            [
                InlineKeyboardButton("📅 This Month", callback_data="stats_month"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def data_management() -> InlineKeyboardMarkup:
        """Data management options"""
        keyboard = [
            [
                InlineKeyboardButton("📋 Data Summary", callback_data="data_summary"),
                InlineKeyboardButton("🗑️ Clear Today", callback_data="clear_today")
            ],
            [
                InlineKeyboardButton("⚠️ Clear All Data", callback_data="clear_all_confirm")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def clear_confirmation(action: str) -> InlineKeyboardMarkup:
        """Confirmation keyboard for data clearing"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes, Clear", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ Cancel", callback_data="manage_data")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
