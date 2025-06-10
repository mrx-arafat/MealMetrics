import base64
import io
import re
from PIL import Image
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error converting image to base64: {e}")
        raise

def pil_image_to_base64(image: Image.Image, format: str = "JPEG") -> str:
    """Convert PIL Image to base64 string"""
    try:
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error converting PIL image to base64: {e}")
        raise

def resize_image_if_needed(image: Image.Image, max_size: tuple = (1024, 1024)) -> Image.Image:
    """Resize image if it's larger than max_size while maintaining aspect ratio"""
    if image.size[0] <= max_size[0] and image.size[1] <= max_size[1]:
        return image
    
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    return image

def format_calories(calories: float) -> str:
    """Format calories for display"""
    if calories == int(calories):
        return f"{int(calories)} calories"
    return f"{calories:.1f} calories"

def get_current_date() -> str:
    """Get current date in YYYY-MM-DD format"""
    return date.today().isoformat()

def get_current_datetime() -> str:
    """Get current datetime in ISO format"""
    return datetime.now().isoformat()

def validate_image_format(filename: str, supported_formats: list) -> bool:
    """Check if image format is supported"""
    if not filename:
        return False
    
    extension = filename.lower().split('.')[-1]
    return extension in [fmt.lower() for fmt in supported_formats]

def format_meal_summary(meals: List[Dict[str, Any]]) -> str:
    """Format a list of meals into a summary string"""
    if not meals:
        return "📊 **Today's Summary**\n\n🍽️ No meals logged today.\n\nSend me a photo of your meal to get started!"

    total_calories = sum(meal['calories'] for meal in meals)
    meal_count = len(meals)

    summary = f"📊 **Today's Summary**\n\n"
    summary += f"🍽️ **Meals logged:** {meal_count}\n"
    summary += f"🔥 **Total calories:** {format_calories(total_calories)}\n\n"

    if meal_count > 0:
        summary += "**Recent meals:**\n"
        for i, meal in enumerate(meals[-5:], 1):  # Show last 5 meals
            try:
                time_str = datetime.fromisoformat(meal['timestamp']).strftime("%H:%M")
                description = escape_markdown_v2(meal['description'][:50] + "..." if len(meal['description']) > 50 else meal['description'])
                summary += f"{i}\\. {description} \\- {format_calories(meal['calories'])} \\({time_str}\\)\n"
            except Exception as e:
                logger.warning(f"Error formatting meal {i}: {e}")
                continue

    return summary

def escape_markdown_v2(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2"""
    if not text:
        return ""

    # Characters that need to be escaped in MarkdownV2
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

    for char in special_chars:
        text = text.replace(char, f'\\{char}')

    return text

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input text"""
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())

    # Limit length
    if len(text) > max_length:
        text = text[:max_length] + "..."

    return text

def parse_numeric_value(value: Union[str, int, float], default: float = 0.0) -> float:
    """Parse numeric values that might contain text like '100 calories' or '85%'"""
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        # Extract first number from string (handles "100 calories", "85%", etc.)
        numbers = re.findall(r'\d+\.?\d*', str(value))
        if numbers:
            return float(numbers[0])
        else:
            logger.warning(f"Could not parse numeric value from '{value}', using default {default}")
            return default

    return default

def validate_user_input(text: str, min_length: int = 1, max_length: int = 1000) -> bool:
    """Validate user input text"""
    if not text or not isinstance(text, str):
        return False

    text = text.strip()
    return min_length <= len(text) <= max_length

def format_confidence(confidence: float) -> str:
    """Format confidence percentage for display"""
    if confidence >= 90:
        return f"🟢 {confidence:.0f}% (Very High)"
    elif confidence >= 75:
        return f"🟡 {confidence:.0f}% (High)"
    elif confidence >= 60:
        return f"🟠 {confidence:.0f}% (Medium)"
    else:
        return f"🔴 {confidence:.0f}% (Low)"
