import base64
import io
from PIL import Image
from datetime import datetime, date
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

def format_meal_summary(meals: list) -> str:
    """Format a list of meals into a summary string"""
    if not meals:
        return "No meals logged today."
    
    total_calories = sum(meal['calories'] for meal in meals)
    meal_count = len(meals)
    
    summary = f"📊 Today's Summary:\n"
    summary += f"🍽️ Meals logged: {meal_count}\n"
    summary += f"🔥 Total calories: {format_calories(total_calories)}\n\n"
    
    summary += "Recent meals:\n"
    for i, meal in enumerate(meals[-5:], 1):  # Show last 5 meals
        time_str = datetime.fromisoformat(meal['timestamp']).strftime("%H:%M")
        summary += f"{i}. {meal['description']} - {format_calories(meal['calories'])} ({time_str})\n"
    
    return summary
