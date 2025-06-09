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
        
    def analyze_food_image(self, image: Image.Image) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Analyze a food image and return calorie estimation
        
        Returns:
            Tuple of (analysis_result, error_message)
        """
        try:
            # Resize image if needed to reduce API costs and improve processing
            processed_image = resize_image_if_needed(image, max_size=(1024, 1024))
            
            # Convert image to base64
            image_base64 = pil_image_to_base64(processed_image, format="JPEG")
            
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
                                "text": CALORIE_ANALYSIS_PROMPT
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
                "max_tokens": 1000,
                "temperature": 0.3  # Lower temperature for more consistent results
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
        """Format analysis result for user display"""
        try:
            # Escape special markdown characters in the description
            description = analysis['description'].replace('*', '\\*').replace('_', '\\_').replace('[', '\\[').replace(']', '\\]')

            message = f"🍽️ *{description}*\n\n"
            message += f"🔥 *Estimated Calories:* {analysis['total_calories']:.0f}\n"
            message += f"📊 *Confidence:* {analysis['confidence']:.0f}%\n\n"

            if 'food_items' in analysis and analysis['food_items']:
                message += "*Breakdown:*\n"
                for item in analysis['food_items']:
                    item_name = item['name'].replace('*', '\\*').replace('_', '\\_')
                    portion = item.get('portion', 'unknown portion').replace('*', '\\*').replace('_', '\\_')
                    message += f"• {item_name} ({portion}): {item['calories']} cal\n"
                message += "\n"

            if 'notes' in analysis and analysis['notes']:
                notes = analysis['notes'].replace('*', '\\*').replace('_', '\\_')
                message += f"*Notes:* {notes}\n\n"

            message += "Would you like to log this meal? 📝"

            return message

        except Exception as e:
            logger.error(f"Error formatting analysis for user: {e}")
            return f"🍽️ Meal analyzed: {analysis.get('total_calories', 0):.0f} calories\nWould you like to log this meal?"
