#!/usr/bin/env python3
"""
Street View Image Collector for EV Charging Station Site Analysis
Collects Google Street View images in a grid pattern around Orcutt, California
for diagonal parking detection and EV charging station site recommendation.
"""

import requests
import os
import time
import math
import csv
from datetime import datetime
from typing import List, Tuple, Dict
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class StreetViewCollector:
    def __init__(self, api_key: str, base_output_dir: str = "site_data"):
        """
        Initialize the Street View collector.
        
        Args:
            api_key: Google Maps API key with Street View Static API enabled
            base_output_dir: Base directory to store collected images and metadata
        """
        self.api_key = api_key
        self.base_output_dir = base_output_dir
        self.base_url = "https://maps.googleapis.com/maps/api/streetview"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Create directory structure
        self._create_directories()
        
        # Image collection parameters
        self.image_size = "640x640"
        self.image_format = "jpg"
        self.fov = 90  # Field of view in degrees
        self.angles = [0, 90, 180, 270]  # Multiple angles per location
        
        # Metadata tracking
        self.collection_metadata = []
        
    def _create_directories(self):
        """Create the directory structure for organizing collected data."""
        directories = [
            os.path.join(self.base_output_dir, "raw_images"),
            os.path.join(self.base_output_dir, "processed_images", "train", "diagonal_parking"),
            os.path.join(self.base_output_dir, "processed_images", "train", "no_diagonal_parking"),
            os.path.join(self.base_output_dir, "processed_images", "validation"),
            os.path.join(self.base_output_dir, "processed_images", "test"),
            os.path.join(self.base_output_dir, "metadata")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        self.logger.info(f"Created directory structure in {self.base_output_dir}")
    
    def generate_grid_coordinates(self, 
                                center_lat: float, 
                                center_lon: float, 
                                area_square_miles: float = 5.0,
                                grid_spacing_feet: float = 350) -> List[Tuple[float, float]]:
        """
        Generate a grid of coordinates covering the specified area.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            area_square_miles: Total area to cover in square miles
            grid_spacing_feet: Spacing between grid points in feet
            
        Returns:
            List of (latitude, longitude) tuples
        """
        # Convert area to approximate radius in miles
        radius_miles = math.sqrt(area_square_miles / math.pi) / 2
        
        # Convert to degrees (rough approximation)
        # 1 degree latitude ≈ 69 miles
        # 1 degree longitude ≈ 69 * cos(latitude) miles
        lat_degree_miles = 69.0
        lon_degree_miles = 69.0 * math.cos(math.radians(center_lat))
        
        radius_lat = radius_miles / lat_degree_miles
        radius_lon = radius_miles / lon_degree_miles
        
        # Convert grid spacing from feet to degrees
        grid_spacing_miles = grid_spacing_feet / 5280.0
        lat_spacing = grid_spacing_miles / lat_degree_miles
        lon_spacing = grid_spacing_miles / lon_degree_miles
        
        coordinates = []
        
        # Generate grid points
        lat = center_lat - radius_lat
        while lat <= center_lat + radius_lat:
            lon = center_lon - radius_lon
            while lon <= center_lon + radius_lon:
                # Check if point is within circular area
                lat_dist = (lat - center_lat) * lat_degree_miles
                lon_dist = (lon - center_lon) * lon_degree_miles
                distance = math.sqrt(lat_dist**2 + lon_dist**2)
                
                if distance <= radius_miles:
                    coordinates.append((lat, lon))
                
                lon += lon_spacing
            lat += lat_spacing
        
        self.logger.info(f"Generated {len(coordinates)} grid coordinates")
        return coordinates
    
    def collect_street_view_image(self, 
                                lat: float, 
                                lon: float, 
                                heading: int,
                                location_id: str) -> Dict:
        """
        Collect a single street view image from the specified location and heading.
        
        Args:
            lat: Latitude
            lon: Longitude
            heading: Compass heading (0-359 degrees)
            location_id: Unique identifier for this location
            
        Returns:
            Dictionary with collection metadata
        """
        params = {
            'size': self.image_size,
            'location': f"{lat},{lon}",
            'heading': heading,
            'fov': self.fov,
            'format': self.image_format,
            'key': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{location_id}_h{heading:03d}_{timestamp}.{self.image_format}"
            filepath = os.path.join(self.base_output_dir, "raw_images", filename)
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Collect metadata
            metadata = {
                'filename': filename,
                'filepath': filepath,
                'latitude': lat,
                'longitude': lon,
                'heading': heading,
                'fov': self.fov,
                'timestamp': timestamp,
                'location_id': location_id,
                'file_size_bytes': len(response.content),
                'success': True,
                'error_message': None
            }
            
            self.logger.info(f"Successfully collected: {filename}")
            return metadata
            
        except requests.exceptions.RequestException as e:
            error_metadata = {
                'filename': None,
                'filepath': None,
                'latitude': lat,
                'longitude': lon,
                'heading': heading,
                'fov': self.fov,
                'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
                'location_id': location_id,
                'file_size_bytes': 0,
                'success': False,
                'error_message': str(e)
            }
            
            self.logger.error(f"Failed to collect image for {location_id}, heading {heading}: {e}")
            return error_metadata
    
    def collect_location_images(self, 
                              lat: float, 
                              lon: float, 
                              location_id: str,
                              delay_seconds: float = 0.1) -> List[Dict]:
        """
        Collect images from all angles for a single location.
        
        Args:
            lat: Latitude
            lon: Longitude
            location_id: Unique identifier for this location
            delay_seconds: Delay between API calls to respect rate limits
            
        Returns:
            List of metadata dictionaries for each image
        """
        location_metadata = []
        
        for heading in self.angles:
            metadata = self.collect_street_view_image(lat, lon, heading, location_id)
            location_metadata.append(metadata)
            self.collection_metadata.append(metadata)
            
            # Respect API rate limits
            if delay_seconds > 0:
                time.sleep(delay_seconds)
        
        return location_metadata
    
    def collect_area_images(self, 
                          center_lat: float, 
                          center_lon: float,
                          area_square_miles: float = 5.0,
                          grid_spacing_feet: float = 350,
                          delay_seconds: float = 0.1) -> str:
        """
        Collect street view images for the entire specified area.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            area_square_miles: Total area to cover in square miles
            grid_spacing_feet: Spacing between grid points in feet
            delay_seconds: Delay between API calls
            
        Returns:
            Path to the metadata CSV file
        """
        self.logger.info(f"Starting area collection centered at ({center_lat}, {center_lon})")
        self.logger.info(f"Area: {area_square_miles} sq miles, Grid spacing: {grid_spacing_feet} feet")
        
        # Generate coordinate grid
        coordinates = self.generate_grid_coordinates(
            center_lat, center_lon, area_square_miles, grid_spacing_feet
        )
        
        total_locations = len(coordinates)
        total_images = total_locations * len(self.angles)
        
        self.logger.info(f"Will collect {total_images} images from {total_locations} locations")
        
        # Collect images for each location
        for i, (lat, lon) in enumerate(coordinates, 1):
            location_id = f"orcutt_{i:04d}"
            
            self.logger.info(f"Processing location {i}/{total_locations}: {location_id}")
            
            try:
                self.collect_location_images(lat, lon, location_id, delay_seconds)
            except Exception as e:
                self.logger.error(f"Error processing location {location_id}: {e}")
                continue
        
        # Save metadata
        metadata_file = self.save_metadata()
        
        # Print collection summary
        successful_images = sum(1 for m in self.collection_metadata if m['success'])
        failed_images = len(self.collection_metadata) - successful_images
        
        self.logger.info(f"Collection complete!")
        self.logger.info(f"Successful images: {successful_images}")
        self.logger.info(f"Failed images: {failed_images}")
        self.logger.info(f"Metadata saved to: {metadata_file}")
        
        return metadata_file
    
    def save_metadata(self) -> str:
        """Save collection metadata to CSV file."""
        metadata_file = os.path.join(
            self.base_output_dir, 
            "metadata", 
            f"collection_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if self.collection_metadata:
            fieldnames = self.collection_metadata[0].keys()
            
            with open(metadata_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.collection_metadata)
        
        return metadata_file


def main():
    """
    Main function to run the street view collection for Orcutt, California.
    """
    # Load API key from environment variable
    API_KEY = os.getenv('google_maps_street_view_api')
    
    # Orcutt, California coordinates
    CENTER_LAT = 34.865838
    CENTER_LON = -120.447520
    
    # Collection parameters
    AREA_SQUARE_MILES = 3.5
    GRID_SPACING_FEET = 350  # Approximately 300-400 sq ft per grid cell
    DELAY_SECONDS = 0.1  # Rate limiting delay
    
    # Validate API key
    if not API_KEY:
        print("ERROR: Google Maps API key not found!")
        print("Please check that:")
        print("1. You have a .env file in the current directory")
        print("2. The .env file contains: google_maps_street_view_api=YOUR_API_KEY")
        print("3. You have enabled the Street View Static API in Google Cloud Console")
        return
    
    # Initialize collector
    collector = StreetViewCollector(API_KEY)
    
    # Start collection
    try:
        metadata_file = collector.collect_area_images(
            CENTER_LAT, 
            CENTER_LON, 
            AREA_SQUARE_MILES, 
            GRID_SPACING_FEET,
            DELAY_SECONDS
        )
        
        print(f"\nCollection completed successfully!")
        print(f"Images saved to: {collector.base_output_dir}/raw_images/")
        print(f"Metadata saved to: {metadata_file}")
        print(f"\nNext steps:")
        print("1. Review collected images")
        print("2. Start manual labeling process")
        print("3. Organize images into train/validation/test sets")
        
    except KeyboardInterrupt:
        print("\nCollection interrupted by user")
    except Exception as e:
        print(f"Error during collection: {e}")
        logging.exception("Collection failed with exception")


if __name__ == "__main__":
    main()
