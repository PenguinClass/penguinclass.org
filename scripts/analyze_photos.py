#!/usr/bin/env python3
"""
Comprehensive photo analysis for the Penguin Class gallery.

This script:
1. Finds all photos in archive/legacy-website and Jekyll site
2. Deduplicates by filename and size
3. Extracts metadata (EXIF, file info)
4. Organizes by event/year/category
5. Generates gallery data structure
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
from datetime import datetime

# Photo extensions to look for
PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}

# Directories to analyze
ARCHIVE_DIR = Path("archive/legacy-website")
JEKYLL_DIR = Path("pages/gallery")
ASSETS_DIR = Path("assets/images")

class PhotoAnalyzer:
    def __init__(self):
        self.photos = []
        self.duplicates = []
        self.categories = defaultdict(list)
        self.events = defaultdict(list)
        self.years = defaultdict(list)
        
    def get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file for deduplication."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def extract_metadata(self, file_path: Path) -> Dict:
        """Extract metadata from photo file."""
        stat = file_path.stat()
        
        metadata = {
            'filename': file_path.name,
            'path': str(file_path),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': file_path.suffix.lower(),
            'hash': self.get_file_hash(file_path),
            'source': 'archive' if 'archive' in str(file_path) else 'jekyll'
        }
        
        # Try to extract year from filename or path
        year_match = re.search(r'\b(19|20)\d{2}\b', file_path.name)
        if year_match:
            metadata['year'] = int(year_match.group())
        else:
            # Try to extract from path
            path_year_match = re.search(r'\b(19|20)\d{2}\b', str(file_path))
            if path_year_match:
                metadata['year'] = int(path_year_match.group())
        
        # Try to extract event information
        filename_lower = file_path.name.lower()
        path_lower = str(file_path).lower()
        
        # Common event keywords
        event_keywords = [
            'international', 'championship', 'champ', 'north american', 'na',
            'annual', 'regatta', 'frostbite', 'heritage', 'turkey trot',
            'spring', 'summer', 'fall', 'winter', 'tayc', 'cryc', 'giys',
            'beachwood', 'corsica', 'admiral byrd', 'meyers'
        ]
        
        for keyword in event_keywords:
            if keyword in filename_lower or keyword in path_lower:
                metadata['event_keyword'] = keyword
                break
        
        return metadata
    
    def categorize_photo(self, metadata: Dict) -> List[str]:
        """Categorize photo based on filename and path."""
        categories = []
        filename = metadata['filename'].lower()
        path = metadata['path'].lower()
        
        # Event-based categories
        if any(word in filename or word in path for word in ['international', 'champ']):
            categories.append('Championships')
        elif any(word in filename or word in path for word in ['annual', 'regatta']):
            categories.append('Regattas')
        elif any(word in filename or word in path for word in ['frostbite']):
            categories.append('Frostbite')
        elif any(word in filename or word in path for word in ['heritage']):
            categories.append('Heritage')
        
        # Location-based categories
        if any(word in filename or word in path for word in ['tayc', 'tred avon']):
            categories.append('TAYC')
        elif any(word in filename or word in path for word in ['cryc', 'corsica']):
            categories.append('CRYC')
        elif any(word in filename or word in path for word in ['giys', 'greenwich']):
            categories.append('GIYS')
        elif any(word in filename or word in path for word in ['beachwood']):
            categories.append('Beachwood')
        
        # Type-based categories
        if any(word in filename or word in path for word in ['boat', 'sail', 'rigging']):
            categories.append('Boats')
        elif any(word in filename or word in path for word in ['people', 'crew', 'sailor']):
            categories.append('People')
        elif any(word in filename or word in path for word in ['award', 'trophy', 'prize']):
            categories.append('Awards')
        
        # Default category
        if not categories:
            categories.append('General')
        
        return categories
    
    def find_photos(self) -> List[Dict]:
        """Find all photos in the specified directories."""
        all_photos = []
        
        # Search archive directory
        if ARCHIVE_DIR.exists():
            for file_path in ARCHIVE_DIR.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in PHOTO_EXTENSIONS:
                    metadata = self.extract_metadata(file_path)
                    all_photos.append(metadata)
        
        # Search Jekyll gallery directory
        if JEKYLL_DIR.exists():
            for file_path in JEKYLL_DIR.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in PHOTO_EXTENSIONS:
                    metadata = self.extract_metadata(file_path)
                    all_photos.append(metadata)
        
        # Search assets directory
        if ASSETS_DIR.exists():
            for file_path in ASSETS_DIR.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in PHOTO_EXTENSIONS:
                    metadata = self.extract_metadata(file_path)
                    all_photos.append(metadata)
        
        return all_photos
    
    def deduplicate_photos(self, photos: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Remove duplicate photos based on filename and size."""
        seen = {}
        unique_photos = []
        duplicates = []
        
        for photo in photos:
            # Create a key based on filename and size
            key = (photo['filename'], photo['size'])
            
            if key in seen:
                # This is a duplicate
                duplicates.append(photo)
                print(f"Duplicate found: {photo['filename']} ({photo['size']} bytes)")
                print(f"  Original: {seen[key]['path']}")
                print(f"  Duplicate: {photo['path']}")
            else:
                seen[key] = photo
                unique_photos.append(photo)
        
        return unique_photos, duplicates
    
    def organize_photos(self, photos: List[Dict]):
        """Organize photos by categories, events, and years."""
        for photo in photos:
            # Add to year-based organization
            if 'year' in photo:
                self.years[photo['year']].append(photo)
            
            # Add to event-based organization
            if 'event_keyword' in photo:
                self.events[photo['event_keyword']].append(photo)
            
            # Add to category-based organization
            categories = self.categorize_photo(photo)
            for category in categories:
                self.categories[category].append(photo)
    
    def generate_gallery_data(self) -> Dict:
        """Generate structured data for the gallery."""
        return {
            'total_photos': len(self.photos),
            'total_duplicates': len(self.duplicates),
            'categories': dict(self.categories),
            'events': dict(self.events),
            'years': dict(self.years),
            'photos': self.photos
        }
    
    def analyze(self):
        """Run the complete analysis."""
        print("🔍 Finding all photos...")
        all_photos = self.find_photos()
        print(f"Found {len(all_photos)} total photos")
        
        print("\n🔄 Deduplicating photos...")
        unique_photos, duplicates = self.deduplicate_photos(all_photos)
        print(f"After deduplication: {len(unique_photos)} unique photos")
        print(f"Removed {len(duplicates)} duplicates")
        
        self.photos = unique_photos
        self.duplicates = duplicates
        
        print("\n📊 Organizing photos...")
        self.organize_photos(unique_photos)
        
        print(f"\n📁 Categories found: {len(self.categories)}")
        for category, photos in self.categories.items():
            print(f"  {category}: {len(photos)} photos")
        
        print(f"\n🏆 Events found: {len(self.events)}")
        for event, photos in self.events.items():
            print(f"  {event}: {len(photos)} photos")
        
        print(f"\n📅 Years found: {len(self.years)}")
        for year in sorted(self.years.keys()):
            print(f"  {year}: {len(self.years[year])} photos")
        
        return self.generate_gallery_data()

def main():
    analyzer = PhotoAnalyzer()
    gallery_data = analyzer.analyze()
    
    # Save the analysis results
    with open('gallery_analysis.json', 'w') as f:
        json.dump(gallery_data, f, indent=2)
    
    print(f"\n💾 Analysis saved to gallery_analysis.json")
    
    # Generate a summary report
    print(f"\n📋 SUMMARY REPORT")
    print(f"Total photos found: {gallery_data['total_photos']}")
    print(f"Duplicates removed: {gallery_data['total_duplicates']}")
    print(f"Unique photos: {gallery_data['total_photos'] - gallery_data['total_duplicates']}")
    print(f"Categories: {len(gallery_data['categories'])}")
    print(f"Events: {len(gallery_data['events'])}")
    print(f"Years: {len(gallery_data['years'])}")

if __name__ == "__main__":
    main()
