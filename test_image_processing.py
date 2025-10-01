#!/usr/bin/env python3
"""
Test script to diagnose image processing issues in MealMetrics bot

This script helps identify which step in the image processing pipeline is failing
for problematic images.
"""

import sys
import os
import logging
from PIL import Image

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import enhance_image_for_analysis, pil_image_to_base64, resize_image_if_needed
from ai.vision_analyzer import VisionAnalyzer

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def test_image_file(image_path: str):
    """
    Test an image file through the entire processing pipeline
    
    Args:
        image_path: Path to the image file to test
    """
    print("=" * 80)
    print(f"Testing image: {image_path}")
    print("=" * 80)
    
    # Step 1: Check if file exists
    print("\n[Step 1] Checking if file exists...")
    if not os.path.exists(image_path):
        print(f"❌ ERROR: File not found: {image_path}")
        return False
    print(f"✅ File exists: {image_path}")
    
    # Step 2: Try to open the image
    print("\n[Step 2] Opening image with PIL...")
    try:
        with Image.open(image_path) as image:
            print(f"✅ Image opened successfully")
            print(f"   - Size: {image.size}")
            print(f"   - Mode: {image.mode}")
            print(f"   - Format: {image.format}")
            
            # Step 3: Convert to RGB if needed
            print("\n[Step 3] Converting to RGB if needed...")
            if image.mode != 'RGB':
                print(f"   Converting from {image.mode} to RGB...")
                image = image.convert('RGB')
                print(f"✅ Converted to RGB")
            else:
                print(f"✅ Already in RGB mode")
            
            # Step 4: Test resize function
            print("\n[Step 4] Testing resize function...")
            try:
                resized = resize_image_if_needed(image, max_size=(1024, 1024))
                print(f"✅ Resize successful")
                print(f"   - Original size: {image.size}")
                print(f"   - Resized to: {resized.size}")
            except Exception as e:
                print(f"❌ Resize failed: {e}")
                return False
            
            # Step 5: Test image enhancement
            print("\n[Step 5] Testing image enhancement...")
            try:
                enhanced = enhance_image_for_analysis(image)
                print(f"✅ Enhancement successful")
                print(f"   - Enhanced image size: {enhanced.size}")
                print(f"   - Enhanced image mode: {enhanced.mode}")
            except Exception as e:
                print(f"❌ Enhancement failed: {e}")
                logger.exception("Enhancement error details:")
                print("\n⚠️  Trying without enhancement...")
                enhanced = image
            
            # Step 6: Test base64 conversion
            print("\n[Step 6] Testing base64 conversion...")
            try:
                base64_str = pil_image_to_base64(enhanced, format="JPEG")
                print(f"✅ Base64 conversion successful")
                print(f"   - Base64 length: {len(base64_str)} characters")
            except Exception as e:
                print(f"❌ Base64 conversion failed: {e}")
                return False
            
            # Step 7: Test AI analysis (optional - requires API key)
            print("\n[Step 7] Testing AI analysis...")
            try:
                analyzer = VisionAnalyzer()
                print("   Sending to AI for analysis (this may take a moment)...")
                result, error = analyzer.analyze_food_image(enhanced)
                
                if error:
                    print(f"❌ AI analysis returned error: {error}")
                    return False
                elif result:
                    print(f"✅ AI analysis successful")
                    print(f"   - Description: {result.get('description', 'N/A')}")
                    print(f"   - Calories: {result.get('total_calories', 'N/A')}")
                    print(f"   - Confidence: {result.get('confidence', 'N/A')}%")
                else:
                    print(f"❌ AI analysis returned no result")
                    return False
                    
            except Exception as e:
                print(f"❌ AI analysis failed: {e}")
                logger.exception("AI analysis error details:")
                return False
            
    except IOError as e:
        print(f"❌ Failed to open image: {e}")
        logger.exception("Image open error details:")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("Unexpected error details:")
        return False
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    return True


def main():
    """Main entry point"""
    print("🍽️ MealMetrics - Image Processing Test Tool")
    print("=" * 80)
    
    if len(sys.argv) < 2:
        print("Usage: python test_image_processing.py <image_path>")
        print("\nExample:")
        print("  python test_image_processing.py /path/to/food_photo.jpg")
        print("\nThis tool will test your image through all processing steps:")
        print("  1. File existence check")
        print("  2. Image opening with PIL")
        print("  3. RGB conversion")
        print("  4. Image resizing")
        print("  5. Image enhancement")
        print("  6. Base64 conversion")
        print("  7. AI analysis (requires API key)")
        return 1
    
    image_path = sys.argv[1]
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\n⚠️  WARNING: .env file not found!")
        print("AI analysis (Step 7) will fail without API credentials.")
        print("Steps 1-6 will still be tested.\n")
    
    success = test_image_file(image_path)
    
    if success:
        print("\n✅ Image processing test completed successfully!")
        return 0
    else:
        print("\n❌ Image processing test failed!")
        print("Check the error messages above to identify the issue.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

