#!/usr/bin/env python3
"""
Example usage of the Street View Collector for Orcutt, California
This script demonstrates how to use the collector with different parameters.
"""

from street_view_collector import StreetViewCollector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_small_test_collection():
    """Run a small test collection with just a few points."""
    print("Running small test collection...")
    
    # Load API key from environment
    API_KEY = os.getenv('google_maps_street_view_api')
    
    if not API_KEY:
        print("ERROR: Google Maps API key not found!")
        print("Please check your .env file contains: google_maps_street_view_api=YOUR_API_KEY")
        return
    
    # Initialize collector
    collector = StreetViewCollector(API_KEY, base_output_dir="test_collection")
    
    # Test with a very small area first
    test_coordinates = [
        (34.865838, -120.447520),  # Center point
        (34.866000, -120.447000),  # Slightly north and east
        (34.865600, -120.448000),  # Slightly south and west
    ]
    
    print(f"Testing with {len(test_coordinates)} locations")
    
    for i, (lat, lon) in enumerate(test_coordinates, 1):
        location_id = f"test_{i:02d}"
        print(f"Collecting images for location {i}: {location_id}")
        
        try:
            metadata = collector.collect_location_images(lat, lon, location_id, delay_seconds=0.5)
            successful = sum(1 for m in metadata if m['success'])
            print(f"  Success: {successful}/4 images")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Save test metadata
    metadata_file = collector.save_metadata()
    print(f"\nTest complete! Metadata saved to: {metadata_file}")

def run_full_orcutt_collection():
    """Run the full Orcutt area collection."""
    print("Running full Orcutt collection...")
    
    # Load API key from environment
    API_KEY = os.getenv('google_maps_street_view_api')
    
    if not API_KEY:
        print("ERROR: Google Maps API key not found!")
        print("Please check your .env file contains: google_maps_street_view_api=YOUR_API_KEY")
        return
    
    # Initialize collector
    collector = StreetViewCollector(API_KEY)
    
    # Orcutt area parameters
    CENTER_LAT = 34.865838
    CENTER_LON = -120.447520
    AREA_SQUARE_MILES = 3.5
    GRID_SPACING_FEET = 350
    
    print(f"Starting collection for {AREA_SQUARE_MILES} square miles around Orcutt")
    print(f"Center: ({CENTER_LAT}, {CENTER_LON})")
    print(f"Grid spacing: {GRID_SPACING_FEET} feet")
    
    try:
        metadata_file = collector.collect_area_images(
            CENTER_LAT, 
            CENTER_LON, 
            AREA_SQUARE_MILES, 
            GRID_SPACING_FEET,
            delay_seconds=0.1
        )
        
        print(f"\nFull collection completed!")
        print(f"Metadata file: {metadata_file}")
        
    except Exception as e:
        print(f"Collection failed: {e}")

def estimate_api_costs():
    """Estimate Google Street View API costs for the collection."""
    # Street View Static API pricing (as of 2024)
    COST_PER_REQUEST = 0.007  # $0.007 per request
    
    # Calculate grid size
    area_sq_miles = 3.5
    grid_spacing_feet = 350
    
    # Rough calculation
    area_sq_feet = area_sq_miles * (5280 ** 2)  # Convert to square feet
    grid_cell_area = grid_spacing_feet ** 2
    num_locations = area_sq_feet / grid_cell_area
    
    # 4 images per location (4 angles)
    total_requests = num_locations * 4
    estimated_cost = total_requests * COST_PER_REQUEST
    
    print(f"Estimated API Usage:")
    print(f"  Area: {area_sq_miles} square miles")
    print(f"  Grid spacing: {grid_spacing_feet} feet")
    print(f"  Estimated locations: {num_locations:.0f}")
    print(f"  Total API requests: {total_requests:.0f}")
    print(f"  Estimated cost: ${estimated_cost:.2f}")
    print(f"\nNote: This is a rough estimate. Actual costs may vary.")

if __name__ == "__main__":
    print("Street View Collection Examples for Orcutt, California")
    print("=" * 55)
    
    while True:
        print("\nOptions:")
        print("1. Run small test collection (3 locations)")
        print("2. Run full Orcutt area collection")
        print("3. Estimate API costs")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            run_small_test_collection()
        elif choice == "2":
            run_full_orcutt_collection()
        elif choice == "3":
            estimate_api_costs()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
