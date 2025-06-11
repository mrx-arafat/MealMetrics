#!/usr/bin/env python3
"""
Test photo analysis with the enhanced response system
"""

import sys
import os
from PIL import Image
import io
import base64

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.vision_analyzer import VisionAnalyzer


def create_test_image():
    """Create a simple test image for analysis"""
    # Create a simple image with food-like colors
    img = Image.new('RGB', (400, 300), color='white')
    
    # Add some colored rectangles to simulate food
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Brown rectangle (rice/grain)
    draw.rectangle([50, 50, 200, 150], fill='#D2B48C')
    
    # Green rectangle (vegetables)
    draw.rectangle([220, 50, 350, 100], fill='#90EE90')
    
    # Orange rectangle (curry/sauce)
    draw.rectangle([220, 120, 350, 170], fill='#FFA500')
    
    # White/cream rectangle (roti/bread)
    draw.rectangle([50, 180, 150, 250], fill='#F5F5DC')
    
    return img


def test_photo_analysis():
    """Test the photo analysis with enhanced response"""
    print("🧪 Testing Photo Analysis with Enhanced Response")
    print("=" * 60)
    
    analyzer = VisionAnalyzer()
    
    # Create test image
    test_image = create_test_image()
    
    print("📸 Created test image simulating rice, vegetables, curry, and roti")
    print("🤖 Analyzing with AI...")
    
    try:
        # Analyze the image
        result, error = analyzer.analyze_food_image(test_image)
        
        if error:
            print(f"❌ Analysis failed: {error}")
            return False
        
        if not result:
            print("❌ No analysis result returned")
            return False
        
        print("\n✅ Analysis successful!")
        print("📊 Raw Analysis Result:")
        print("-" * 40)
        
        for key, value in result.items():
            if key == 'food_items':
                print(f"{key}: {len(value)} items")
                for i, item in enumerate(value, 1):
                    print(f"  {i}. {item.get('name', 'Unknown')} - {item.get('calories', 0):.0f} cal")
            elif isinstance(value, float):
                print(f"{key}: {value:.1f}")
            else:
                print(f"{key}: {value}")
        
        print("\n📝 Formatted User Message:")
        print("-" * 40)
        formatted_message = analyzer.format_analysis_for_user(result)
        print(formatted_message)
        
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_photo_analysis()
    print("\n" + "=" * 60)
    if success:
        print("✅ Photo analysis test passed!")
        print("🚀 The bot should now show detailed breakdowns for all photos!")
    else:
        print("❌ Photo analysis test failed!")
        print("🔧 Check the logs for more details.")
