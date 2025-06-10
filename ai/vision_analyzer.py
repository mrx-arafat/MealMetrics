import json
import logging
import requests
from PIL import Image
from typing import Dict, Any, Optional, Tuple
from utils.config import Config
from utils.helpers import pil_image_to_base64, resize_image_if_needed
from .prompts import CALORIE_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

class VisionAnalyzer:
    """AI-powered food image analysis for calorie estimation"""
    
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.OPENROUTER_MODEL
        self.base_url = Config.OPENROUTER_BASE_URL
        
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
            # Resize image if needed to reduce API costs and improve processing
            processed_image = resize_image_if_needed(image, max_size=(1024, 1024))
            
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
                "max_tokens": 1500,  # Increased for more detailed analysis
                "temperature": 0.2   # Even lower temperature for more consistent results with context
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return None, error_msg
            
            # Parse response
            response_data = response.json()
            
            if 'choices' not in response_data or not response_data['choices']:
                error_msg = "No response from AI model"
                logger.error(error_msg)
                return None, error_msg
            
            ai_response = response_data['choices'][0]['message']['content']
            
            # Try to parse JSON response
            try:
                # Clean the response - remove markdown code blocks if present
                cleaned_response = ai_response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]  # Remove ```json
                if cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:]   # Remove ```
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]  # Remove trailing ```

                # Extract JSON from response (in case there's extra text)
                json_start = cleaned_response.find('{')
                json_end = cleaned_response.rfind('}') + 1

                if json_start == -1 or json_end == 0:
                    # Fallback: try to parse the entire response
                    analysis_result = json.loads(cleaned_response)
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

                # Set default values for new optional fields if missing
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
                
                # Ensure numeric fields are properly typed
                analysis_result['total_calories'] = float(analysis_result['total_calories'])
                analysis_result['confidence'] = float(analysis_result['confidence'])
                
                # Validate ranges
                if analysis_result['confidence'] < 0 or analysis_result['confidence'] > 100:
                    analysis_result['confidence'] = max(0, min(100, analysis_result['confidence']))
                
                if analysis_result['total_calories'] < 0:
                    analysis_result['total_calories'] = 0
                
                logger.info(f"Successfully analyzed food image: {analysis_result['description']} "
                           f"({analysis_result['total_calories']} cal, {analysis_result['confidence']}% confidence)")
                
                return analysis_result, None
                
            except json.JSONDecodeError as e:
                # Try to handle incomplete JSON by attempting to complete it
                try:
                    # If the JSON is incomplete, try to extract what we can
                    if '"total_calories"' in cleaned_response and '"confidence"' in cleaned_response:
                        # Try to extract basic info even if JSON is incomplete
                        import re

                        # Extract description
                        desc_match = re.search(r'"description":\s*"([^"]*)"', cleaned_response)
                        description = desc_match.group(1) if desc_match else "Food item"

                        # Extract total calories
                        cal_match = re.search(r'"total_calories":\s*(\d+)', cleaned_response)
                        total_calories = float(cal_match.group(1)) if cal_match else 100

                        # Extract confidence
                        conf_match = re.search(r'"confidence":\s*(\d+)', cleaned_response)
                        confidence = float(conf_match.group(1)) if conf_match else 70

                        # Create a basic analysis result
                        analysis_result = {
                            "description": description,
                            "total_calories": total_calories,
                            "confidence": confidence,
                            "food_items": [],
                            "notes": "Analysis completed with partial data due to response formatting"
                        }

                        logger.warning(f"Recovered partial data from incomplete JSON response")
                        return analysis_result, None

                except Exception as recovery_error:
                    logger.error(f"Failed to recover from JSON error: {recovery_error}")

                error_msg = f"Failed to parse AI response as JSON: {e}\nResponse: {ai_response[:500]}..."
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
        """Format enhanced analysis result for user display"""
        try:
            # Escape special markdown characters
            def escape_markdown(text):
                if not text:
                    return ""
                return str(text).replace('*', '\\*').replace('_', '\\_').replace('[', '\\[').replace(']', '\\]')

            description = escape_markdown(analysis['description'])

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
                user_ack = escape_markdown(analysis['user_input_acknowledged'])
                message += f"✅ *Analyzing your:* {user_ack}\n\n"

            message += f"{health_emoji} *{description}*\n\n"

            # Add special warning banner for junk food
            if health_category == 'junk':
                message += "🚨 *WARNING: HIGH-RISK FOOD DETECTED* 🚨\n"
                message += "⚠️ *This meal may significantly impact your health* ⚠️\n\n"

            # Calories and health score with enhanced impact for junk food
            message += f"🔥 *Calories:* {analysis['total_calories']:.0f}\n"

            # Enhanced health score display based on category
            if health_category == 'junk':
                if health_score <= 3:
                    health_display = f"💀 *Health Score:* {health_score}/10 {'💀' * min(health_score, 3)} - DANGER ZONE"
                else:
                    health_display = f"⚠️ *Health Score:* {health_score}/10 {'⚠️' * min(health_score, 3)} - PROCEED WITH CAUTION"
            elif health_category == 'healthy':
                health_display = f"💚 *Health Score:* {health_score}/10 {'⭐' * min(health_score, 5)} - EXCELLENT CHOICE"
            else:
                health_display = f"💛 *Health Score:* {health_score}/10 {'⭐' * min(health_score, 5)}"

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
                    item_name = escape_markdown(item['name'])
                    portion = escape_markdown(item.get('portion', 'unknown portion'))
                    calories = item.get('calories', 0)
                    cooking_method = escape_markdown(item.get('cooking_method', ''))
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
                    message += f"   🔥 {calories} cal"
                    if cooking_method:
                        message += f" • 👨‍🍳 {cooking_method}"
                    message += f" • {health_indicator}\n"
                message += "\n"

            # Enhanced witty comment section with darker reality checks for junk food
            if analysis.get('witty_comment'):
                witty_comment = escape_markdown(analysis['witty_comment'])
                if health_category == 'junk':
                    message += f"💀 *REALITY CHECK:* {witty_comment}\n\n"
                elif health_category == 'healthy':
                    message += f"🌟 *Great Choice!* {witty_comment}\n\n"
                else:
                    message += f"💡 *Nutritional Insight:* {witty_comment}\n\n"

            # Enhanced recommendations with urgent warnings for junk food
            if analysis.get('recommendations'):
                recommendations = escape_markdown(analysis['recommendations'])
                if health_category == 'junk':
                    message += f"🚨 *URGENT - YOUR HEALTH DEPENDS ON THIS:* {recommendations}\n\n"
                elif health_category == 'healthy':
                    message += f"✨ *Keep It Up:* {recommendations}\n\n"
                else:
                    message += f"🎯 *Suggestions:* {recommendations}\n\n"

            # Fun fact with enhanced presentation
            if analysis.get('fun_fact'):
                fun_fact = escape_markdown(analysis['fun_fact'])
                message += f"🤓 *Did You Know?* {fun_fact}\n\n"

            # Additional notes with enhanced formatting
            if analysis.get('notes'):
                notes = escape_markdown(analysis['notes'])
                message += f"📝 *Additional Notes:* {notes}\n\n"

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
