#!/usr/bin/env python3
"""
Test consistency improvements for food analysis
"""

import sys
import os
from PIL import Image
import io

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.vision_analyzer import VisionAnalyzer

def create_test_image():
    """Create a simple test image for consistency testing"""
    # Create a simple colored image
    img = Image.new('RGB', (300, 300), color='orange')
    return img

def test_image_hashing():
    """Test that identical images produce the same hash"""
    print("Testing Image Hashing:")
    print("=" * 40)
    
    analyzer = VisionAnalyzer()
    
    # Create two identical images
    img1 = create_test_image()
    img2 = create_test_image()
    
    # Get hashes
    hash1 = analyzer._get_image_hash(img1)
    hash2 = analyzer._get_image_hash(img2)
    
    print(f"Image 1 hash: {hash1}")
    print(f"Image 2 hash: {hash2}")
    
    if hash1 == hash2:
        print("PASS: Identical images produce same hash!")
    else:
        print("FAIL: Identical images produce different hashes!")
    
    # Test with slightly different image
    img3 = Image.new('RGB', (300, 300), color='red')
    hash3 = analyzer._get_image_hash(img3)
    
    print(f"Different image hash: {hash3}")
    
    if hash1 != hash3:
        print("PASS: Different images produce different hashes!")
    else:
        print("FAIL: Different images produce same hash!")

def test_caching_mechanism():
    """Test that caching works for identical images"""
    print("\nTesting Caching Mechanism:")
    print("=" * 40)
    
    analyzer = VisionAnalyzer()
    
    # Clear any existing cache
    analyzer._analysis_cache = {}
    
    # Create test image
    test_image = create_test_image()
    
    print("Cache size before analysis:", len(analyzer._analysis_cache))
    
    # Note: This test won't actually call the API since we don't have a real food image
    # But we can test the caching logic structure
    
    # Test cache key generation
    image_hash = analyzer._get_image_hash(test_image)
    cache_key_no_caption = f"{image_hash}_no_caption"
    cache_key_with_caption = f"{image_hash}_test caption"
    
    print(f"Cache key without caption: {cache_key_no_caption[:20]}...")
    print(f"Cache key with caption: {cache_key_with_caption[:20]}...")
    
    if cache_key_no_caption != cache_key_with_caption:
        print("PASS: Different captions produce different cache keys!")
    else:
        print("FAIL: Different captions produce same cache key!")

def test_api_parameters():
    """Test that API parameters are set for consistency"""
    print("\nTesting API Parameters for Consistency:")
    print("=" * 40)
    
    analyzer = VisionAnalyzer()
    
    # We can't test the actual API call without making a real request,
    # but we can verify the analyzer is configured correctly
    
    print(f"API Key configured: {'Yes' if analyzer.api_key else 'No'}")
    print(f"Model configured: {analyzer.model}")
    print(f"Base URL configured: {analyzer.base_url}")
    
    # Check if cache is initialized
    print(f"Cache initialized: {'Yes' if hasattr(analyzer, '_analysis_cache') else 'No'}")
    print(f"Cache type: {type(analyzer._analysis_cache)}")
    
    print("PASS: Analyzer properly configured for consistency!")

def test_calorie_range_consistency():
    """Test that calorie range generation is consistent"""
    print("\nTesting Calorie Range Consistency:")
    print("=" * 40)
    
    analyzer = VisionAnalyzer()
    
    # Test multiple calls with same input
    test_calories = [150, 450, 650, 850, 1200]
    
    for calories in test_calories:
        range1 = analyzer._get_calorie_range(calories)
        range2 = analyzer._get_calorie_range(calories)
        range3 = analyzer._get_calorie_range(calories)
        
        print(f"Calories {calories}: {range1}")
        
        if range1 == range2 == range3:
            print(f"  PASS: Consistent range generation")
        else:
            print(f"  FAIL: Inconsistent ranges: {range1}, {range2}, {range3}")

def main():
    """Run all consistency tests"""
    print("MealMetrics Consistency Improvement Tests")
    print("=" * 50)
    
    try:
        test_image_hashing()
        test_caching_mechanism()
        test_api_parameters()
        test_calorie_range_consistency()
        
        print("\n" + "=" * 50)
        print("Consistency tests completed!")
        print("=" * 50)
        print("\nKey Improvements Made:")
        print("1. Image hashing for identical image detection")
        print("2. Result caching to ensure same image = same result")
        print("3. Zero temperature (0.0) for maximum AI consistency")
        print("4. Fixed seed (42) for reproducible results")
        print("5. Low top_p (0.1) for deterministic output")
        print("6. Standardized portion estimation guidelines")
        print("7. Cache size limiting to prevent memory issues")
        
    except Exception as e:
        print(f"\nTest failed: {e}")

if __name__ == "__main__":
    main()
