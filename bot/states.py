from enum import Enum

class ConversationState(Enum):
    """Conversation states for the bot"""
    IDLE = "idle"
    WAITING_FOR_IMAGE = "waiting_for_image"
    PROCESSING_IMAGE = "processing_image"
    WAITING_FOR_CONFIRMATION = "waiting_for_confirmation"
    VIEWING_HISTORY = "viewing_history"
    VIEWING_STATS = "viewing_stats"

class CallbackData:
    """Constants for callback data patterns"""
    
    # Meal actions
    LOG_MEAL = "log_meal"
    CANCEL_MEAL = "cancel_meal"
    
    # Navigation
    MAIN_MENU = "main_menu"
    BACK = "back"
    
    # Summary and stats
    TODAY_SUMMARY = "today_summary"
    WEEKLY_STATS = "weekly_stats"
    STATS_TODAY = "stats_today"
    STATS_WEEK = "stats_week"
    STATS_MONTH = "stats_month"
    
    # History
    VIEW_HISTORY = "view_history"
    HISTORY_PREV = "history_prev"
    HISTORY_NEXT = "history_next"
    
    # Help
    HELP = "help"
    HELP_USAGE = "help_usage"
    HELP_TROUBLESHOOT = "help_troubleshoot"
    HELP_ACCURACY = "help_accuracy"

    # Data Management
    MANAGE_DATA = "manage_data"
    DATA_SUMMARY = "data_summary"
    CLEAR_TODAY = "clear_today"
    CLEAR_RANGE = "clear_range"
    CLEAR_ALL_CONFIRM = "clear_all_confirm"
    CONFIRM_CLEAR_TODAY = "confirm_clear_today"
    CONFIRM_CLEAR_ALL = "confirm_clear_all"
    
    @staticmethod
    def parse_callback(callback_data: str) -> tuple:
        """Parse callback data into action and parameters"""
        parts = callback_data.split(":")
        action = parts[0]
        params = parts[1:] if len(parts) > 1 else []
        return action, params
