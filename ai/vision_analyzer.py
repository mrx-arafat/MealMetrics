import json
import logging
import requests
import time
import hashlib
from PIL import Image
from typing import Dict, Any, Optional, Tuple
from utils.config import Config
from utils.helpers import pil_image_to_base64, resize_image_if_needed, parse_numeric_value, escape_markdown_safe, enhance_image_for_analysis
from .prompts import CALORIE_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

class VisionAnalyzer:
    """AI-powered food image analysis for calorie estimation"""

    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.OPENROUTER_MODEL
        self.base_url = Config.OPENROUTER_BASE_URL
        # Cache for consistent results on identical images
        self._analysis_cache = {}

    def _get_image_hash(self, image: Image.Image) -> str:
        """Generate a unique hash for the image including metadata"""
        import io
        import time

        # Use original image characteristics for more unique hashing
        img_byte_arr = io.BytesIO()

        # Include original dimensions and current timestamp in hash
        # This prevents different images from having the same hash
        image_info = f"{image.size[0]}x{image.size[1]}_{int(time.time() * 1000)}"

        # Save original image (not resized) for unique hash
        image.save(img_byte_arr, format='JPEG', quality=95)
        img_bytes = img_byte_arr.getvalue()

        # Combine image bytes with metadata for unique hash
        combined_data = img_bytes + image_info.encode('utf-8')
        return hashlib.md5(combined_data).hexdigest()
        
    def analyze_food_image(self, image: Image.Image, caption: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Analyze a food image and return calorie estimation

        Args:
            image: PIL Image object of the food
            caption: Optional user-provided caption with additional details

        Returns:
            Tuple of (analysis_result, error_message)
        """
        try:
            # Enhanced image preprocessing for better AI analysis
            processed_image = enhance_image_for_analysis(image)
            logger.info("Applied advanced image enhancement for optimal AI analysis")

            # CACHE DISABLED: Always analyze fresh to prevent showing wrong results for different photos
            # This ensures each photo gets its own unique analysis
            logger.info("Analyzing fresh image (cache disabled for accuracy)")
            
            # Convert image to base64
            image_base64 = pil_image_to_base64(processed_image, format="JPEG")
            
            # Prepare the enhanced prompt with caption context
            enhanced_prompt = CALORIE_ANALYSIS_PROMPT
            if caption:
                enhanced_prompt += f"""

🚨🚨🚨 OVERRIDE ALL VISUAL ANALYSIS - USER KNOWS BEST 🚨🚨🚨
The user explicitly stated: "{caption}"

🔒 LOCKED-IN FOOD IDENTIFICATION:
- FOOD TYPE: Extract the exact food name from user's caption
- QUANTITY: Use user's specified amount
- MODIFICATIONS: Honor all user specifications

⚠️ CRITICAL RULES - NO EXCEPTIONS:
1. **NEVER CHANGE THE FOOD NAME** - If user says "mango juice", your response MUST say "mango juice"
2. **IGNORE VISUAL CONTRADICTIONS** - Even if image looks like orange juice, it's mango juice if user says so
3. **COPY USER'S EXACT WORDS** - Don't paraphrase or "correct" their food identification
4. **USER IS THE EXPERT** - They know what they're eating better than any AI visual analysis
5. **IMAGE = PORTION SIZE ONLY** - Use visual only for estimating how much, not what it is

🎯 YOUR TASK: Analyze the nutritional content of "{caption}" using the image only to estimate portion size.

DO NOT IDENTIFY THE FOOD FROM THE IMAGE. THE USER ALREADY TOLD YOU WHAT IT IS.
"""

            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": enhanced_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 2500,  # Increased for more detailed analysis
                "temperature": 0.1,  # Zero temperature for maximum consistency
                "seed": 42,          # Fixed seed for reproducible results
                "top_p": 0.1         # Very low top_p for more deterministic output
            }
            
            # ULTRA-SMART: Try multiple AI models for maximum accuracy
            models_to_try = [
                Config.OPENROUTER_MODEL,  # Primary model
                "google/gemini-2.5-flash-preview",  # Backup model 1
                "anthropic/claude-3.5-sonnet",  # Backup model 2
            ]

            successful_response = None
            final_error = None

            for model_index, model in enumerate(models_to_try):
                logger.info(f"🤖 Trying AI model {model_index + 1}/{len(models_to_try)}: {model}")

                # Update payload with current model
                current_payload = payload.copy()
                current_payload["model"] = model

                # Adjust parameters for different models
                if "claude" in model.lower():
                    current_payload["max_tokens"] = 3000
                    current_payload["temperature"] = 0.0
                elif "gemini" in model.lower():
                    current_payload["max_tokens"] = 2500
                    current_payload["temperature"] = 0.1

                # Make API request with retry logic for each model
                max_retries = 2  # Reduced per model, but trying multiple models
                for attempt in range(max_retries):
                    try:
                        response = requests.post(
                            f"{self.base_url}/chat/completions",
                            headers=headers,
                            json=current_payload,
                            timeout=45
                        )

                        if response.status_code == 200:
                            successful_response = response
                            logger.info(f"✅ Success with model: {model}")
                            break
                        elif response.status_code == 429:  # Rate limit
                            if attempt < max_retries - 1:
                                wait_time = (attempt + 1) * 2
                                logger.warning(f"Rate limited on {model}, waiting {wait_time}s before retry {attempt + 1}")
                                time.sleep(wait_time)
                                continue
                        else:
                            error_msg = f"Model {model} failed with status {response.status_code}: {response.text}"
                            logger.warning(error_msg)
                            final_error = error_msg
                            break

                    except requests.exceptions.Timeout:
                        error_msg = f"Model {model} timed out on attempt {attempt + 1}"
                        logger.warning(error_msg)
                        final_error = error_msg
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                        break
                    except requests.exceptions.RequestException as e:
                        error_msg = f"Network error with model {model}: {e}"
                        logger.warning(error_msg)
                        final_error = error_msg
                        break

                # If we got a successful response, break out of model loop
                if successful_response:
                    break

                # If not the last model, wait before trying next
                if model_index < len(models_to_try) - 1:
                    logger.info(f"⏳ Trying next model in 1 second...")
                    time.sleep(1)

            # Check if any model succeeded
            if not successful_response:
                error_msg = f"All AI models failed. Last error: {final_error}"
                logger.error(error_msg)
                return None, error_msg

            response = successful_response

            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON response from API: {e}"
                logger.error(error_msg)
                return None, error_msg

            if 'choices' not in response_data or not response_data['choices']:
                error_msg = "No response from AI model"
                logger.error(error_msg)
                return None, error_msg

            ai_response = response_data['choices'][0]['message']['content']
            
            # Try to parse JSON response with enhanced recovery
            try:
                # Clean the response - remove markdown code blocks if present
                cleaned_response = ai_response.strip()

                # Remove various markdown code block formats
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]
                elif cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:]

                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]

                # Remove any leading/trailing text that's not JSON
                json_start = cleaned_response.find('{')
                json_end = cleaned_response.rfind('}') + 1

                if json_start == -1:
                    raise json.JSONDecodeError("No JSON object found", cleaned_response, 0)

                if json_end <= json_start:
                    # Try to complete incomplete JSON
                    logger.warning("Incomplete JSON detected, attempting to complete it")
                    json_str = cleaned_response[json_start:]

                    # Try to fix common incomplete JSON patterns
                    if not json_str.rstrip().endswith('}'):
                        # Handle incomplete strings first
                        if json_str.count('"') % 2 != 0:
                            # Odd number of quotes means unterminated string
                            json_str += '"'
                            logger.info("Added closing quote for unterminated string")

                        # Handle incomplete arrays
                        open_brackets = json_str.count('[') - json_str.count(']')
                        if open_brackets > 0:
                            json_str += ']' * open_brackets
                            logger.info(f"Added {open_brackets} closing brackets")

                        # Handle incomplete objects
                        open_braces = json_str.count('{') - json_str.count('}')
                        if open_braces > 0:
                            json_str += '}' * open_braces
                            logger.info(f"Added {open_braces} closing braces")

                    analysis_result = json.loads(json_str)
                else:
                    json_str = cleaned_response[json_start:json_end]
                    analysis_result = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['description', 'total_calories', 'confidence']
                for field in required_fields:
                    if field not in analysis_result:
                        error_msg = f"Missing required field in AI response: {field}"
                        logger.error(error_msg)
                        return None, error_msg

                # Set default values for missing fields and enhance basic responses
                if 'health_category' not in analysis_result:
                    analysis_result['health_category'] = 'moderate'
                if 'health_score' not in analysis_result:
                    analysis_result['health_score'] = 5
                if 'witty_comment' not in analysis_result:
                    analysis_result['witty_comment'] = ''
                if 'recommendations' not in analysis_result:
                    analysis_result['recommendations'] = ''
                if 'fun_fact' not in analysis_result:
                    analysis_result['fun_fact'] = ''
                if 'total_carbs' not in analysis_result:
                    analysis_result['total_carbs'] = 0
                if 'total_protein' not in analysis_result:
                    analysis_result['total_protein'] = 0
                if 'total_fat' not in analysis_result:
                    analysis_result['total_fat'] = 0

                # Enhance basic responses with estimated detailed breakdown
                if 'food_items' not in analysis_result or not analysis_result['food_items']:
                    # Create food items from description if missing
                    description = analysis_result.get('description', 'Food item')
                    total_calories = analysis_result.get('total_calories', 0)

                    # Split description into food items
                    food_names = [item.strip() for item in description.split(',')]
                    if len(food_names) == 1 and ',' not in description:
                        # Single item, use full calories
                        food_items = [{
                            "name": food_names[0],
                            "portion": "estimated portion",
                            "calories": total_calories,
                            "carbs": total_calories * 0.5 / 4,  # Rough estimate: 50% carbs
                            "protein": total_calories * 0.2 / 4,  # 20% protein
                            "fat": total_calories * 0.3 / 9,     # 30% fat
                            "cooking_method": "prepared",
                            "health_score": analysis_result.get('health_score', 5)
                        }]
                    else:
                        # Multiple items, distribute calories
                        calories_per_item = total_calories / len(food_names) if food_names else total_calories
                        food_items = []
                        for name in food_names:
                            food_items.append({
                                "name": name,
                                "portion": "estimated portion",
                                "calories": calories_per_item,
                                "carbs": calories_per_item * 0.5 / 4,
                                "protein": calories_per_item * 0.2 / 4,
                                "fat": calories_per_item * 0.3 / 9,
                                "cooking_method": "prepared",
                                "health_score": analysis_result.get('health_score', 5)
                            })

                    analysis_result['food_items'] = food_items
                    logger.info("Enhanced basic response with estimated food breakdown")

                # Add estimated macronutrients if missing
                if analysis_result.get('total_carbs', 0) == 0 and analysis_result.get('total_calories', 0) > 0:
                    total_cal = analysis_result['total_calories']
                    analysis_result['total_carbs'] = total_cal * 0.5 / 4  # 50% carbs
                    analysis_result['total_protein'] = total_cal * 0.2 / 4  # 20% protein
                    analysis_result['total_fat'] = total_cal * 0.3 / 9     # 30% fat
                    logger.info("Added estimated macronutrient breakdown")

                # Add contextual content if missing
                if not analysis_result.get('witty_comment'):
                    calories = analysis_result.get('total_calories', 0)
                    health_category = analysis_result.get('health_category', 'moderate')

                    if health_category == 'junk' or calories > 800:
                        analysis_result['witty_comment'] = "That's quite a calorie-dense choice! Your future self might have some words about this decision."
                    elif health_category == 'healthy' or calories < 300:
                        analysis_result['witty_comment'] = "Great choice! Your body will thank you for this nutritious fuel."
                    else:
                        analysis_result['witty_comment'] = "A balanced meal that fits well into a healthy eating pattern."

                if not analysis_result.get('recommendations'):
                    health_category = analysis_result.get('health_category', 'moderate')

                    if health_category == 'junk':
                        analysis_result['recommendations'] = "Consider balancing this with extra vegetables and water. Maybe plan a lighter next meal?"
                    elif health_category == 'healthy':
                        analysis_result['recommendations'] = "Keep up the great choices! This meal provides good nutrition and energy."
                    else:
                        analysis_result['recommendations'] = "Try adding more vegetables or lean protein to boost the nutritional value."

                if not analysis_result.get('fun_fact'):
                    analysis_result['fun_fact'] = "Did you know? It takes about 20 minutes for your brain to register that you're full, so eating slowly can help with portion control!"
                
                # Ensure numeric fields are properly typed with robust parsing
                analysis_result['total_calories'] = parse_numeric_value(analysis_result['total_calories'], 0.0)
                analysis_result['confidence'] = parse_numeric_value(analysis_result['confidence'], 70.0)

                # Parse numeric fields in food_items if they exist
                if 'food_items' in analysis_result and analysis_result['food_items']:
                    for item in analysis_result['food_items']:
                        if 'calories' in item:
                            item['calories'] = parse_numeric_value(item.get('calories', 0), 0.0)
                        if 'carbs' in item:
                            item['carbs'] = parse_numeric_value(item.get('carbs', 0), 0.0)
                        if 'protein' in item:
                            item['protein'] = parse_numeric_value(item.get('protein', 0), 0.0)
                        if 'fat' in item:
                            item['fat'] = parse_numeric_value(item.get('fat', 0), 0.0)
                        if 'health_score' in item:
                            item['health_score'] = parse_numeric_value(item.get('health_score', 5), 5.0)

                # Parse total macronutrients
                if 'total_carbs' in analysis_result:
                    analysis_result['total_carbs'] = parse_numeric_value(analysis_result.get('total_carbs', 0), 0.0)
                if 'total_protein' in analysis_result:
                    analysis_result['total_protein'] = parse_numeric_value(analysis_result.get('total_protein', 0), 0.0)
                if 'total_fat' in analysis_result:
                    analysis_result['total_fat'] = parse_numeric_value(analysis_result.get('total_fat', 0), 0.0)
                if 'health_score' in analysis_result:
                    analysis_result['health_score'] = parse_numeric_value(analysis_result.get('health_score', 5), 5.0)
                
                # Validate ranges
                if analysis_result['confidence'] < 0 or analysis_result['confidence'] > 100:
                    analysis_result['confidence'] = max(0, min(100, analysis_result['confidence']))
                
                if analysis_result['total_calories'] < 0:
                    analysis_result['total_calories'] = 0
                
                # Cache disabled - each photo gets fresh analysis for accuracy

                # Debug logging to see what fields we actually got
                available_fields = list(analysis_result.keys())
                logger.info(f"Successfully analyzed food image: {analysis_result['description']} "
                           f"({analysis_result['total_calories']} cal, {analysis_result['confidence']}% confidence)")
                logger.debug(f"Analysis result fields: {available_fields}")

                # Check if we have detailed fields
                has_detailed_fields = any(field in analysis_result for field in ['food_items', 'witty_comment', 'recommendations', 'total_carbs'])
                if not has_detailed_fields:
                    logger.warning("AI response missing detailed fields - may show basic format only")

                return analysis_result, None
                
            except json.JSONDecodeError as e:
                # Enhanced recovery for incomplete or malformed JSON
                logger.warning(f"JSON parsing failed: {e}, attempting recovery")

                try:
                    # Try multiple recovery strategies
                    analysis_result = None

                    # Strategy 1: Extract from partial JSON using regex
                    if '"description"' in ai_response and '"total_calories"' in ai_response:
                        import re

                        # Extract description
                        desc_match = re.search(r'"description":\s*"([^"]*)"', ai_response)
                        description = desc_match.group(1) if desc_match else "Food item"

                        # Extract total calories (handle both integer and float)
                        cal_match = re.search(r'"total_calories":\s*(\d+(?:\.\d+)?)', ai_response)
                        total_calories = float(cal_match.group(1)) if cal_match else 150

                        # Extract confidence
                        conf_match = re.search(r'"confidence":\s*(\d+(?:\.\d+)?)', ai_response)
                        confidence = float(conf_match.group(1)) if conf_match else 70

                        # Try to extract food items
                        food_items = []
                        food_items_match = re.search(r'"food_items":\s*\[(.*?)\]', ai_response, re.DOTALL)
                        if food_items_match:
                            items_text = food_items_match.group(1)
                            # Extract individual food items
                            item_matches = re.finditer(r'\{[^}]*"name":\s*"([^"]*)"[^}]*"calories":\s*(\d+(?:\.\d+)?)[^}]*\}', items_text)
                            for item_match in item_matches:
                                food_items.append({
                                    "name": item_match.group(1),
                                    "calories": float(item_match.group(2)),
                                    "portion": "estimated portion"
                                })

                        analysis_result = {
                            "description": description,
                            "total_calories": total_calories,
                            "confidence": confidence,
                            "food_items": food_items,
                            "notes": "Analysis recovered from partial response"
                        }

                        logger.info(f"Successfully recovered analysis from partial JSON: {description}")

                    # Strategy 2: Create minimal fallback response
                    if not analysis_result:
                        # Extract any food-related text for description
                        food_keywords = ['food', 'meal', 'dish', 'drink', 'coffee', 'tea', 'juice', 'sandwich', 'salad', 'soup', 'rice', 'chicken', 'beef', 'fish']
                        description = "Food item"

                        for keyword in food_keywords:
                            if keyword.lower() in ai_response.lower():
                                description = f"Meal containing {keyword}"
                                break

                        analysis_result = {
                            "description": description,
                            "total_calories": 200,  # Conservative estimate
                            "confidence": 50,       # Low confidence for fallback
                            "food_items": [],
                            "notes": "Fallback analysis due to response parsing issues"
                        }

                        logger.warning("Using fallback analysis due to JSON parsing failure")

                    if analysis_result:
                        return analysis_result, None

                except Exception as recovery_error:
                    logger.error(f"All recovery strategies failed: {recovery_error}")

                error_msg = f"Failed to parse AI response as JSON: {e}\nResponse preview: {ai_response[:200]}..."
                logger.error(error_msg)
                return None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Request to AI service timed out"
            logger.error(error_msg)
            return None, error_msg
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error when calling AI service: {e}"
            logger.error(error_msg)
            return None, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error during image analysis: {e}"
            logger.error(error_msg)
            return None, error_msg
    
    def format_analysis_for_user(self, analysis: Dict[str, Any]) -> str:
        """Format enhanced analysis result for user display with safe markdown"""
        try:
            # Use safe markdown escaping to prevent parsing errors
            def safe_escape(text):
                if not text:
                    return ""
                return escape_markdown_safe(str(text))

            description = safe_escape(analysis['description'])

            # Health category emoji mapping with darker tone for junk food
            health_emojis = {
                'healthy': '🥗',
                'moderate': '🍽️',
                'junk': '☠️'  # Skull emoji for reality check impact
            }

            health_category = analysis.get('health_category', 'moderate')
            health_emoji = health_emojis.get(health_category, '🍽️')
            health_score = analysis.get('health_score', 5)

            # Build message with enhanced formatting
            message = ""

            # Add user input acknowledgment if provided
            if analysis.get('user_input_acknowledged'):
                user_ack = safe_escape(analysis['user_input_acknowledged'])
                message += f"✅ *Analyzing your:* {user_ack}\n\n"

            message += f"{health_emoji} *{description}*\n\n"

            # Add special warning banner for junk food
            if health_category == 'junk':
                message += "🚨 *WARNING: HIGH-RISK FOOD DETECTED* 🚨\n"
                message += "⚠️ *This meal may significantly impact your health* ⚠️\n\n"

            # Calories and health score with enhanced impact for junk food
            message += f"🔥 *Calories:* {analysis['total_calories']:.0f}\n"

            # Enhanced health score display based on category
            health_score_int = int(health_score)  # Convert to int for emoji multiplication
            if health_category == 'junk':
                if health_score <= 3:
                    health_display = f"💀 *Health Score:* {health_score}/10 {'💀' * min(health_score_int, 3)} - DANGER ZONE"
                else:
                    health_display = f"⚠️ *Health Score:* {health_score}/10 {'⚠️' * min(health_score_int, 3)} - PROCEED WITH CAUTION"
            elif health_category == 'healthy':
                health_display = f"💚 *Health Score:* {health_score}/10 {'⭐' * min(health_score_int, 5)} - EXCELLENT CHOICE"
            else:
                health_display = f"💛 *Health Score:* {health_score}/10 {'⭐' * min(health_score_int, 5)}"

            message += f"{health_display}\n"
            message += f"📊 *Confidence:* {analysis['confidence']:.0f}%\n\n"

            # Macronutrients if available
            if analysis.get('total_carbs') or analysis.get('total_protein') or analysis.get('total_fat'):
                message += "*Macronutrients:*\n"
                if analysis.get('total_carbs'):
                    message += f"🍞 Carbs: {analysis['total_carbs']:.0f}g\n"
                if analysis.get('total_protein'):
                    message += f"🥩 Protein: {analysis['total_protein']:.0f}g\n"
                if analysis.get('total_fat'):
                    message += f"🥑 Fat: {analysis['total_fat']:.0f}g\n"
                message += "\n"

            # Detailed food breakdown with enhanced formatting
            if 'food_items' in analysis and analysis['food_items']:
                message += "🍽️ *Detailed Breakdown:*\n"
                for i, item in enumerate(analysis['food_items'], 1):
                    item_name = safe_escape(item['name'])
                    portion = safe_escape(item.get('portion', 'unknown portion'))
                    calories = item.get('calories', 0)
                    cooking_method = safe_escape(item.get('cooking_method', ''))
                    item_health = item.get('health_score', 5)

                    # Enhanced health indicator
                    if item_health >= 8:
                        health_indicator = "🟢 Excellent"
                    elif item_health >= 6:
                        health_indicator = "🟡 Good"
                    elif item_health >= 4:
                        health_indicator = "🟠 Moderate"
                    else:
                        health_indicator = "🔴 Poor"

                    message += f"{i}. **{item_name}** ({portion})\n"
                    message += f"   🔥 {calories:.0f} cal"
                    if cooking_method:
                        message += f" • 👨‍🍳 {cooking_method}"
                    message += f" • {health_indicator}\n"
                message += "\n"

            # Enhanced witty comment section with proper contextualization
            if analysis.get('witty_comment'):
                witty_comment = safe_escape(analysis['witty_comment'])
                # Only show if it's not the generic template text
                if not any(template in witty_comment for template in [
                    "For junk food: Dark reality check",
                    "For healthy food: Positive reinforcement",
                    "For moderate: Balanced perspective"
                ]):
                    if health_category == 'junk':
                        message += f"💀 *REALITY CHECK:* {witty_comment}\n\n"
                    elif health_category == 'healthy':
                        message += f"🌟 *Great Choice!* {witty_comment}\n\n"
                    else:
                        message += f"💡 *Nutritional Insight:* {witty_comment}\n\n"

            # Enhanced recommendations with proper contextualization
            if analysis.get('recommendations'):
                recommendations = safe_escape(analysis['recommendations'])
                # Only show if it's not the generic template text
                if not any(template in recommendations for template in [
                    "For junk food: Stark warnings",
                    "For healthy food: Ways to maintain",
                    "For moderate: Improvement suggestions"
                ]):
                    if health_category == 'junk':
                        message += f"🚨 *URGENT - YOUR HEALTH DEPENDS ON THIS:* {recommendations}\n\n"
                    elif health_category == 'healthy':
                        message += f"✨ *Keep It Up:* {recommendations}\n\n"
                    else:
                        message += f"🎯 *Suggestions:* {recommendations}\n\n"

            # Fun fact with enhanced presentation
            if analysis.get('fun_fact'):
                fun_fact = safe_escape(analysis['fun_fact'])
                message += f"🤓 *Did You Know?* {fun_fact}\n\n"

            # Additional notes with enhanced formatting (commented out for now)
            # if analysis.get('notes'):
            #     notes = escape_markdown(analysis['notes'])
            #     message += f"📝 *Additional Notes:* {notes}\n\n"

            # Add calorie estimation note
            total_calories = analysis.get('total_calories', 0)
            if total_calories > 0:
                calorie_range = self._get_calorie_range(total_calories)
                food_description = analysis.get('description', 'this meal')
                # Don't escape the parentheses in NB note as they don't need escaping in this context
                message += f"*NB:* {calorie_range} (This is an estimate based on a typical serving size of {safe_escape(food_description)}, which may vary depending on preparation method and portion size)\n\n"

            # Enhanced call-to-action with visual separator
            message += "─" * 25 + "\n"
            message += "📝 *Ready to log this meal?*"

            return message

        except Exception as e:
            logger.error(f"Error formatting enhanced analysis for user: {e}")
            # Enhanced fallback message
            return (f"🍽️ *Meal Analysis Complete*\n\n"
                   f"🔥 Calories: {analysis.get('total_calories', 0):.0f}\n"
                   f"📊 Confidence: {analysis.get('confidence', 70):.0f}%\n\n"
                   f"─────────────────────────\n"
                   f"📝 *Ready to log this meal?*")

    def _get_calorie_range(self, calories: float) -> str:
        """Generate a calorie range for the NB note"""
        # Create a range of ±50 calories around the estimate
        lower = max(0, int(calories - 50))
        upper = int(calories + 50)

        # Round to nearest 25 for cleaner ranges
        lower = (lower // 25) * 25
        upper = ((upper + 24) // 25) * 25

        return f"{lower}-{upper} kcal"
