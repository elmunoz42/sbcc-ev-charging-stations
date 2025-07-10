# Configuration file for Street View Collection
# Copy this file to config.py and fill in your actual values

# Google Maps API Configuration
GOOGLE_MAPS_API_KEY = "YOUR_API_KEY_HERE"

# Orcutt, California Target Area
TARGET_COORDINATES = {
    "center_lat": 34.865838,
    "center_lon": -120.447520,
    "area_square_miles": 3.5,
    "grid_spacing_feet": 350
}

# Collection Parameters
COLLECTION_SETTINGS = {
    "image_size": "640x640",
    "image_format": "jpg",
    "field_of_view": 90,
    "headings": [0, 90, 180, 270],  # North, East, South, West
    "delay_seconds": 0.1  # Rate limiting
}

# Directory Structure
DIRECTORIES = {
    "base_output": "site_data",
    "raw_images": "raw_images",
    "processed": "processed_images",
    "metadata": "metadata"
}
