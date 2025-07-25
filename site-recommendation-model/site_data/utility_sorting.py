#!/usr/bin/env python3
"""
Utility script for organizing street view images into training folders.
Copies images from raw_images to processed_images/train/ folders based on labeling.

This script assumes:
1. Images with diagonal parking have been manually moved to processed_images/train/diagonal_parking/
2. All remaining raw images should go to processed_images/train/no_diagonal_parking/
"""

import os
import shutil
import logging
from pathlib import Path

class ImageSorter:
    def __init__(self, base_dir="./"):
        """
        Initialize the image sorter.
        
        Args:
            base_dir: Base directory containing the site_data folder
        """
        self.base_dir = Path(base_dir)
        self.raw_images_dir = self.base_dir / "raw_images"
        self.diagonal_parking_dir = self.base_dir / "processed_images" / "train" / "diagonal_parking"
        self.no_diagonal_parking_dir = self.base_dir / "processed_images" / "train" / "no_diagonal_parking"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Ensure directories exist
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        self.diagonal_parking_dir.mkdir(parents=True, exist_ok=True)
        self.no_diagonal_parking_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info("Ensured all directories exist")
    
    def get_already_sorted_images(self):
        """
        Get list of images already in the diagonal_parking folder.
        
        Returns:
            set: Set of filenames already classified as having diagonal parking
        """
        diagonal_images = set()
        
        if self.diagonal_parking_dir.exists():
            for file_path in self.diagonal_parking_dir.glob("*.jpg"):
                diagonal_images.add(file_path.name)
        
        self.logger.info(f"Found {len(diagonal_images)} images already labeled as diagonal parking")
        return diagonal_images
    
    def get_raw_images(self):
        """
        Get list of all images in the raw_images folder.
        
        Returns:
            list: List of Path objects for raw images
        """
        raw_images = []
        
        if self.raw_images_dir.exists():
            for file_path in self.raw_images_dir.glob("*.jpg"):
                raw_images.append(file_path)
        
        self.logger.info(f"Found {len(raw_images)} raw images")
        return raw_images
    
    def sort_remaining_images(self, dry_run=False):
        """
        Copy images from raw_images to no_diagonal_parking if they're not already 
        in diagonal_parking folder.
        
        Args:
            dry_run: If True, only log what would be done without actually copying
        """
        # Get already sorted images
        diagonal_images = self.get_already_sorted_images()
        
        # Get all raw images
        raw_images = self.get_raw_images()
        
        # Filter out images that are already in diagonal_parking
        images_to_sort = []
        for raw_image in raw_images:
            if raw_image.name not in diagonal_images:
                images_to_sort.append(raw_image)
        
        self.logger.info(f"Found {len(images_to_sort)} images to copy to no_diagonal_parking")
        
        if dry_run:
            self.logger.info("DRY RUN - Would copy the following images:")
            for image_path in images_to_sort:
                self.logger.info(f"  {image_path.name}")
            return len(images_to_sort)
        
        # Copy images to no_diagonal_parking folder
        copied_count = 0
        failed_count = 0
        
        for image_path in images_to_sort:
            try:
                destination = self.no_diagonal_parking_dir / image_path.name
                shutil.copy2(image_path, destination)
                copied_count += 1
                
                if copied_count % 50 == 0:  # Progress update every 50 files
                    self.logger.info(f"Copied {copied_count}/{len(images_to_sort)} images...")
                    
            except Exception as e:
                self.logger.error(f"Failed to copy {image_path.name}: {e}")
                failed_count += 1
        
        self.logger.info(f"Sorting complete!")
        self.logger.info(f"Successfully copied: {copied_count} images")
        self.logger.info(f"Failed to copy: {failed_count} images")
        
        return copied_count
    
    def get_sorting_summary(self):
        """Get a summary of current image distribution."""
        diagonal_count = len(list(self.diagonal_parking_dir.glob("*.jpg"))) if self.diagonal_parking_dir.exists() else 0
        no_diagonal_count = len(list(self.no_diagonal_parking_dir.glob("*.jpg"))) if self.no_diagonal_parking_dir.exists() else 0
        raw_count = len(list(self.raw_images_dir.glob("*.jpg"))) if self.raw_images_dir.exists() else 0
        
        summary = {
            "diagonal_parking": diagonal_count,
            "no_diagonal_parking": no_diagonal_count,
            "raw_images": raw_count,
            "total_processed": diagonal_count + no_diagonal_count
        }
        
        return summary
    
    def print_summary(self):
        """Print a summary of current image distribution."""
        summary = self.get_sorting_summary()
        
        print("\n" + "="*50)
        print("IMAGE SORTING SUMMARY")
        print("="*50)
        print(f"Raw images (unsorted): {summary['raw_images']}")
        print(f"Diagonal parking: {summary['diagonal_parking']}")
        print(f"No diagonal parking: {summary['no_diagonal_parking']}")
        print(f"Total processed: {summary['total_processed']}")
        print("="*50)
        
        if summary['raw_images'] > 0:
            print(f"\nImages ready to sort: {summary['raw_images'] - summary['diagonal_parking']}")


def main():
    """Main function to run the image sorting utility."""
    print("Street View Image Sorting Utility")
    print("This script organizes images for training data preparation")
    
    # Initialize sorter
    sorter = ImageSorter()
    
    # Show current status
    sorter.print_summary()
    
    while True:
        print("\nOptions:")
        print("1. Show current summary")
        print("2. Dry run (see what would be sorted)")
        print("3. Sort remaining images")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            sorter.print_summary()
            
        elif choice == "2":
            print("\nRunning dry run...")
            count = sorter.sort_remaining_images(dry_run=True)
            print(f"\nDry run complete. Would sort {count} images.")
            
        elif choice == "3":
            summary = sorter.get_sorting_summary()
            unsorted_count = summary['raw_images'] - summary['diagonal_parking']
            
            if unsorted_count <= 0:
                print("No images to sort!")
                continue
                
            confirm = input(f"\nThis will copy {unsorted_count} images to no_diagonal_parking folder. Continue? (y/n): ")
            
            if confirm.lower() == 'y':
                print("Sorting images...")
                copied = sorter.sort_remaining_images(dry_run=False)
                print(f"\nSorting complete! Copied {copied} images.")
                sorter.print_summary()
            else:
                print("Sorting cancelled.")
                
        elif choice == "4":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()