import base64
import io
import re
from PIL import Image
from datetime import datetime, date, timezone, timedelta
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

def enhance_image_for_analysis(image: Image.Image) -> Image.Image:
    """
    Enhance image quality for better AI food analysis

    This function applies various image processing techniques to improve
    the clarity and quality of food photos for more accurate AI analysis.
    """
    try:
        from PIL import ImageEnhance, ImageFilter

        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # 1. Resize to optimal size for AI analysis (not too large, not too small)
        # AI models work best with images around 1024x1024
        image = resize_image_if_needed(image, max_size=(1024, 1024))

        # 2. Enhance contrast to make food details more visible
        contrast_enhancer = ImageEnhance.Contrast(image)
        image = contrast_enhancer.enhance(1.2)  # 20% more contrast

        # 3. Enhance color saturation to make food colors more vibrant
        color_enhancer = ImageEnhance.Color(image)
        image = color_enhancer.enhance(1.1)  # 10% more saturation

        # 4. Enhance sharpness to make food textures clearer
        sharpness_enhancer = ImageEnhance.Sharpness(image)
        image = sharpness_enhancer.enhance(1.1)  # 10% more sharpness

        # 5. Slight brightness adjustment if image is too dark
        brightness_enhancer = ImageEnhance.Brightness(image)

        # Calculate average brightness
        import numpy as np
        img_array = np.array(image)
        avg_brightness = np.mean(img_array)

        # If image is too dark (avg < 100), brighten it slightly
        if avg_brightness < 100:
            brightness_factor = min(1.3, 100 / avg_brightness)  # Cap at 30% increase
            image = brightness_enhancer.enhance(brightness_factor)
            logger.debug(f"Enhanced brightness by factor {brightness_factor:.2f}")

        # 6. Apply subtle noise reduction for cleaner image
        # Use a gentle blur and then sharpen to reduce noise while preserving details
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        image = sharpness_enhancer.enhance(1.05)  # Compensate for blur

        logger.info("Image enhanced for AI analysis: contrast, color, sharpness, brightness optimized")
        return image

    except Exception as e:
        logger.warning(f"Image enhancement failed, using original: {e}")
        # Return original image if enhancement fails
        return resize_image_if_needed(image, max_size=(1024, 1024))

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

def format_timestamp_for_user(timestamp_str: str, user_timezone_offset: int = None) -> str:
    """
    Format timestamp for user display with timezone consideration

    Args:
        timestamp_str: ISO format timestamp string
        user_timezone_offset: User's timezone offset in seconds (from Telegram)

    Returns:
        Formatted time string (HH:MM)
    """
    try:
        # Parse the timestamp
        if timestamp_str.endswith('Z'):
            # UTC timestamp
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        elif '+' in timestamp_str or timestamp_str.count('-') > 2:
            # Already has timezone info
            dt = datetime.fromisoformat(timestamp_str)
        else:
            # Assume UTC if no timezone info
            dt = datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc)

        # Convert to user's timezone if offset provided
        if user_timezone_offset is not None:
            user_tz = timezone(timedelta(seconds=user_timezone_offset))
            dt = dt.astimezone(user_tz)

        return dt.strftime("%H:%M")
    except Exception as e:
        logger.warning(f"Error formatting timestamp {timestamp_str}: {e}")
        # Fallback to simple parsing
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', ''))
            return dt.strftime("%H:%M")
        except:
            return "00:00"

def validate_image_format(filename: str, supported_formats: list) -> bool:
    """Check if image format is supported"""
    if not filename:
        return False
    
    extension = filename.lower().split('.')[-1]
    return extension in [fmt.lower() for fmt in supported_formats]

def format_meal_summary(meals: List[Dict[str, Any]], user_timezone_offset: int = None) -> str:
    """
    Format a list of meals into a summary string

    Args:
        meals: List of meal dictionaries
        user_timezone_offset: User's timezone offset in seconds (from Telegram)
    """
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
                # Use the new timezone-aware formatting function
                time_str = format_timestamp_for_user(meal['timestamp'], user_timezone_offset)

                # Truncate description and use simple escaping (not full MarkdownV2)
                description = meal['description'][:50] + "..." if len(meal['description']) > 50 else meal['description']
                # Only escape asterisks and underscores for basic markdown
                description = description.replace('*', '\\*').replace('_', '\\_')

                summary += f"{i}. {description} - {format_calories(meal['calories'])} ({time_str})\n"
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

def escape_markdown_safe(text: str) -> str:
    """Safely escape markdown characters with better error handling"""
    if not text:
        return ""

    try:
        # Convert to string if not already
        text = str(text)

        # Only escape the most problematic characters for basic markdown
        # This is more conservative but safer than full MarkdownV2
        escape_chars = {
            '*': '\\*',
            '_': '\\_',
            '[': '\\[',
            ']': '\\]',
            '`': '\\`'
        }

        for char, escaped in escape_chars.items():
            text = text.replace(char, escaped)

        return text
    except Exception as e:
        logger.warning(f"Error escaping markdown: {e}, returning plain text")
        # Return plain text without any markdown if escaping fails
        return str(text).replace('*', '').replace('_', '').replace('[', '').replace(']', '').replace('`', '')

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
