#!/usr/bin/env python3
"""
Quick test script to verify the Street View Collector setup is working
This will collect one test image to validate your API key and setup.
"""

from street_view_collector import StreetViewCollector
import os
from dotenv import load_dotenv

def test_single_image():
    """Test collecting a single street view image."""
    print("Testing Street View Collector setup...")
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    API_KEY = os.getenv('google_maps_street_view_api')
    
    if not API_KEY:
        print("❌ ERROR: API key not found in .env file")
        return False
    
    print("✓ API key loaded successfully")
    
    # Initialize collector with test directory
    collector = StreetViewCollector(API_KEY, base_output_dir="test_output")
    print("✓ Collector initialized successfully")
    
    # Test coordinates (Orcutt center point)
    test_lat = 34.865838
    test_lon = -120.447520
    
    print(f"Testing image collection at coordinates: {test_lat}, {test_lon}")
    
    try:
        # Collect one image
        metadata = collector.collect_street_view_image(
            lat=test_lat,
            lon=test_lon, 
            heading=0,  # North-facing
            location_id="test_001"
        )
        
        if metadata['success']:
            print("✓ Test image collected successfully!")
            print(f"  Filename: {metadata['filename']}")
            print(f"  File size: {metadata['file_size_bytes']} bytes")
            print(f"  Saved to: {metadata['filepath']}")
            return True
        else:
            print(f"❌ Image collection failed: {metadata['error_message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_single_image()
    
    if success:
        print("\n🎉 Setup test completed successfully!")
        print("Your configuration is ready for full data collection.")
        print("\nNext steps:")
        print("1. Run: python example_usage.py (for interactive options)")
        print("2. Or run: python street_view_collector.py (for full collection)")
    else:
        print("\n❌ Setup test failed.")
        print("Please check your API key and internet connection.")
