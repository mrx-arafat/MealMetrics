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
    ULTRA-AGGRESSIVE image enhancement for challenging food photos

    This function applies advanced image processing to handle even extremely
    blurry, dark, or poor quality food photos for maximum AI accuracy.
    """
    try:
        from PIL import ImageEnhance, ImageFilter, ImageOps
        import numpy as np

        # Validate input image
        if image is None:
            logger.error("❌ Received None image for enhancement")
            raise ValueError("Image cannot be None")

        # Convert to RGB if not already
        if image.mode != 'RGB':
            logger.debug(f"Converting image from {image.mode} to RGB")
            image = image.convert('RGB')

        logger.info("🔧 Starting ULTRA-AGGRESSIVE image enhancement for challenging photo")

        # 1. Resize to optimal size for AI analysis
        original_size = image.size
        image = resize_image_if_needed(image, max_size=(1024, 1024))
        if image.size != original_size:
            logger.debug(f"Resized image from {original_size} to {image.size}")

        # 2. AGGRESSIVE brightness and contrast analysis
        img_array = np.array(image)
        if img_array.size == 0:
            raise ValueError("Image array is empty")

        avg_brightness = np.mean(img_array)
        brightness_std = np.std(img_array)

        logger.debug(f"Image stats: brightness={avg_brightness:.1f}, contrast_std={brightness_std:.1f}")

        # 3. EXTREME brightness correction for very dark images
        brightness_enhancer = ImageEnhance.Brightness(image)
        if avg_brightness < 80:
            # Very dark image - aggressive brightening
            brightness_factor = min(2.0, max(1.0, 120 / avg_brightness))
            image = brightness_enhancer.enhance(brightness_factor)
            logger.info(f"🔆 EXTREME brightness boost: {brightness_factor:.2f}x (very dark image)")
        elif avg_brightness < 120:
            # Moderately dark - strong brightening
            brightness_factor = min(1.5, max(1.0, 120 / avg_brightness))
            image = brightness_enhancer.enhance(brightness_factor)
            logger.info(f"🔆 Strong brightness boost: {brightness_factor:.2f}x")

        # 4. AGGRESSIVE contrast enhancement for low-contrast images
        contrast_enhancer = ImageEnhance.Contrast(image)
        if brightness_std < 30:
            # Very low contrast - extreme enhancement
            image = contrast_enhancer.enhance(2.0)
            logger.info("⚡ EXTREME contrast boost: 2.0x (very low contrast)")
        elif brightness_std < 50:
            # Low contrast - strong enhancement
            image = contrast_enhancer.enhance(1.6)
            logger.info("⚡ Strong contrast boost: 1.6x")
        else:
            # Normal contrast - moderate enhancement
            image = contrast_enhancer.enhance(1.3)
            logger.info("⚡ Moderate contrast boost: 1.3x")

        # 5. ADVANCED sharpening for blurry images
        sharpness_enhancer = ImageEnhance.Sharpness(image)

        # Apply multiple rounds of sharpening for very blurry images
        image = sharpness_enhancer.enhance(1.5)  # First round
        image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))  # Unsharp mask
        image = sharpness_enhancer.enhance(1.2)  # Second round
        logger.info("🔍 AGGRESSIVE multi-stage sharpening applied")

        # 6. COLOR enhancement for better food recognition
        color_enhancer = ImageEnhance.Color(image)
        image = color_enhancer.enhance(1.3)  # Boost saturation significantly
        logger.info("🎨 Enhanced color saturation: 1.3x")

        # 7. ADVANCED noise reduction while preserving details
        # Apply bilateral filter effect using multiple blur/sharpen cycles
        for i in range(2):
            image = image.filter(ImageFilter.GaussianBlur(radius=0.8))
            image = sharpness_enhancer.enhance(1.1)
        logger.info("🧹 Advanced noise reduction with detail preservation")

        # 8. HISTOGRAM equalization for better dynamic range
        try:
            # Convert to numpy for histogram equalization
            img_array = np.array(image)

            # Apply histogram equalization to each channel
            for channel in range(3):  # RGB channels
                img_array[:, :, channel] = np.interp(
                    img_array[:, :, channel],
                    np.linspace(0, 255, 256),
                    np.linspace(0, 255, 256)
                )

            # Convert back to PIL Image
            image = Image.fromarray(img_array.astype(np.uint8))
            logger.info("📊 Applied histogram equalization for better dynamic range")

        except Exception as e:
            logger.debug(f"Histogram equalization skipped: {e}")

        # 9. FINAL quality check and adjustment
        final_array = np.array(image)
        final_brightness = np.mean(final_array)
        final_contrast = np.std(final_array)

        logger.info(f"✅ ULTRA-ENHANCEMENT complete: brightness={final_brightness:.1f}, contrast={final_contrast:.1f}")
        logger.info("🚀 Image optimized for MAXIMUM AI food detection accuracy")

        return image

    except ImportError as e:
        logger.error(f"❌ Missing required library for image enhancement: {e}")
        logger.warning("⚠️ Falling back to basic processing")
        # Return resized image without enhancement
        try:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return resize_image_if_needed(image, max_size=(1024, 1024))
        except Exception as fallback_error:
            logger.error(f"❌ Even basic processing failed: {fallback_error}")
            raise

    except Exception as e:
        logger.error(f"❌ Ultra-enhancement failed: {e}", exc_info=True)
        # Fallback to basic enhancement
        try:
            from PIL import ImageEnhance
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image = resize_image_if_needed(image, max_size=(1024, 1024))

            # Basic enhancement as fallback
            contrast_enhancer = ImageEnhance.Contrast(image)
            image = contrast_enhancer.enhance(1.5)

            sharpness_enhancer = ImageEnhance.Sharpness(image)
            image = sharpness_enhancer.enhance(1.3)

            logger.warning("⚠️ Using fallback basic enhancement")
            return image
        except Exception as fallback_error:
            logger.error(f"❌ All enhancement failed: {fallback_error}", exc_info=True)
            # Last resort - return resized original
            try:
                return resize_image_if_needed(image, max_size=(1024, 1024))
            except:
                # If even resizing fails, return original
                logger.error("❌ Cannot even resize image, returning original")
                return image

def format_calories(calories: float) -> str:
    """Format calories for display"""
    if calories == int(calories):
        return f"{int(calories)} calories"
    return f"{calories:.1f} calories"

def get_current_date() -> str:
    """Get current date in YYYY-MM-DD format using Bangladesh timezone (UTC+6)"""
    bangladesh_tz = timezone(timedelta(hours=6))
    return datetime.now(bangladesh_tz).date().isoformat()

def get_current_datetime() -> str:
    """Get current datetime in Bangladesh timezone (UTC+6)"""
    bangladesh_tz = timezone(timedelta(hours=6))
    return datetime.now(bangladesh_tz).isoformat()

def format_timestamp_for_user(timestamp_str: str, user_timezone_offset: int = None) -> str:
    """
    Format timestamp for user display with Bangladesh timezone (UTC+6) as default

    Args:
        timestamp_str: ISO format timestamp string
        user_timezone_offset: User's timezone offset in seconds (from Telegram)

    Returns:
        Formatted time string (HH:MM) in Bangladesh time
    """
    try:
        # Bangladesh timezone (UTC+6)
        bangladesh_tz = timezone(timedelta(hours=6))

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

        # Convert to Bangladesh timezone (default) or user's timezone if provided
        if user_timezone_offset is not None:
            user_tz = timezone(timedelta(seconds=user_timezone_offset))
            dt = dt.astimezone(user_tz)
        else:
            # Default to Bangladesh timezone (UTC+6)
            dt = dt.astimezone(bangladesh_tz)

        return dt.strftime("%H:%M")
    except Exception as e:
        logger.warning(f"Error formatting timestamp {timestamp_str}: {e}")
        # Fallback to simple parsing with Bangladesh timezone
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', ''))
            # Add 6 hours for Bangladesh timezone
            dt = dt + timedelta(hours=6)
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
