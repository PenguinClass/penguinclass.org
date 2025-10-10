#!/usr/bin/env python3
"""
Generate structured gallery data for the photo and video gallery system.

This script creates a comprehensive JSON file with all media metadata
organized for easy browsing and searching.
"""

import json
from pathlib import Path
from typing import Dict
import sys
sys.path.append(str(Path(__file__).parent))
from lib.gallery_importer import GalleryImporter

class MediaAnalyzer:
    """Simplified media analyzer that uses the common GalleryImporter."""
    
    def __init__(self):
        self.importer = GalleryImporter()
    
    def load_analysis_data(self) -> Dict:
        """Load the photo analysis data."""
        analysis_file = Path("tmp/gallery_analysis.json")
        if not analysis_file.exists():
            print("Error: tmp/gallery_analysis.json not found. Run analyze_photos.py first.")
            return {}
        
        with open(analysis_file, 'r') as f:
            return json.load(f)
    
    def analyze(self):
        """Run the complete analysis."""
        print("Loading media analysis data...")
        analysis_data = self.load_analysis_data()
        
        if not analysis_data:
            return {}
        
        print("Generating enhanced gallery data structure...")
        gallery_data = self.importer.generate_gallery_data(analysis_data)
        
        return gallery_data

def main():
    analyzer = MediaAnalyzer()
    gallery_data = analyzer.analyze()
    
    if not gallery_data:
        print("No data to process.")
        return
    
    # Save the gallery data
    output_file = Path("assets/data/gallery.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(gallery_data, f, indent=2)
    
    print(f"Enhanced gallery data saved to {output_file}")
    
    # Print summary
    stats = gallery_data['stats']
    print(f"\n📊 Gallery Summary:")
    print(f"Total media: {stats['total_media']}")
    print(f"Photos: {stats['photos']}")
    print(f"Videos: {stats['videos']}")
    print(f"External videos: {stats['external_videos']}")
    print(f"Duplicates removed: {stats['total_duplicates_removed']}")
    print(f"Years: {stats['years_count']}")
    print(f"Events: {stats['events_count']}")
    print(f"Date range: {stats['date_range']['earliest']} - {stats['date_range']['latest']}")
    
    # Print credit statistics
    credits = stats['credits']
    print(f"\n📸 Credit Statistics:")
    print(f"Credited media: {credits['total_credited']}")
    print(f"Unknown credits: {credits['total_unknown']}")
    print(f"Unique credits: {credits['unique_credits']}")
    print(f"Top credits:")
    for credit, count in credits['top_credits'][:5]:
        print(f"  - {credit}: {count} items")
    
    # Print collection summaries
    print(f"\n📁 Collections:")
    for name, collection in gallery_data['collections'].items():
        print(f"  {collection['title']}: {len(collection['media'])} items")

if __name__ == "__main__":
    main()