#!/usr/bin/env python3
"""
Deduplicate gallery data by removing duplicate media items based on file path.

This script removes duplicate entries from gallery.json, keeping only the first
occurrence of each unique file path.
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class GalleryDeduplicator:
    def __init__(self, gallery_path: str):
        self.gallery_path = Path(gallery_path)
        self.backup_path = None
        
    def create_backup(self):
        """Create a backup of the gallery file before deduplication."""
        if self.gallery_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.backup_path = self.gallery_path.with_name(f'{self.gallery_path.stem}.{timestamp}-backup.json')
            self.gallery_path.rename(self.backup_path)
            print(f"Created backup: {self.backup_path}")
            return True
        return False
    
    def deduplicate_gallery(self, create_backup: bool = True) -> dict:
        """Remove duplicate media items from gallery data."""
        if create_backup:
            self.create_backup()
        
        # Load gallery data from backup if it exists, otherwise from original
        source_path = self.backup_path if self.backup_path else self.gallery_path
        if not source_path.exists():
            raise FileNotFoundError(f"Gallery file not found: {source_path}")
        
        with open(source_path, 'r', encoding='utf-8') as f:
            gallery_data = json.load(f)
        
        # Track duplicates
        seen_paths = set()
        duplicates = []
        unique_items = []
        
        # Process media items
        for item in gallery_data.get('media_index', []):
            path = item.get('path', '')
            if path in seen_paths:
                duplicates.append(item)
                print(f"Removing duplicate: {path}")
            else:
                seen_paths.add(path)
                unique_items.append(item)
        
        # Update gallery data
        gallery_data['media_index'] = unique_items
        
        # Update statistics
        original_count = len(gallery_data.get('media_index', [])) + len(duplicates)
        gallery_data['stats']['total_media'] = len(unique_items)
        gallery_data['stats']['total_duplicates_removed'] = gallery_data['stats'].get('total_duplicates_removed', 0) + len(duplicates)
        
        # Rebuild categories, years, and events
        self._rebuild_indexes(gallery_data)
        
        # Save deduplicated data
        with open(self.gallery_path, 'w', encoding='utf-8') as f:
            json.dump(gallery_data, f, indent=2, ensure_ascii=False)
        
        print(f"Deduplication complete:")
        print(f"  Original items: {original_count}")
        print(f"  Unique items: {len(unique_items)}")
        print(f"  Duplicates removed: {len(duplicates)}")
        print(f"  Saved to: {self.gallery_path}")
        
        return {
            'original_count': original_count,
            'unique_count': len(unique_items),
            'duplicates_removed': len(duplicates),
            'backup_path': str(self.backup_path) if self.backup_path else None
        }
    
    def _rebuild_indexes(self, gallery_data: dict):
        """Rebuild categories, years, and events indexes after deduplication."""
        categories = defaultdict(list)
        years = defaultdict(list)
        events = defaultdict(list)
        
        for item in gallery_data['media_index']:
            # Add to categories
            for category in item.get('categories', []):
                categories[category].append(item)
            
            # Add to years
            year = item.get('year')
            if year:
                years[year].append(item)
            
            # Add to events
            event = item.get('event')
            if event:
                events[event].append(item)
        
        # Update gallery data
        gallery_data['categories'] = dict(categories)
        gallery_data['years'] = dict(years)
        gallery_data['events'] = dict(events)
        
        # Update stats
        gallery_data['stats']['categories_count'] = len(categories)
        gallery_data['stats']['years_count'] = len(years)
        gallery_data['stats']['events_count'] = len(events)

def main():
    parser = argparse.ArgumentParser(description='Deduplicate gallery data')
    parser.add_argument('--gallery-path', default='assets/data/gallery.json',
                       help='Path to gallery.json file')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backup before deduplication')
    
    args = parser.parse_args()
    
    deduplicator = GalleryDeduplicator(args.gallery_path)
    
    try:
        result = deduplicator.deduplicate_gallery(create_backup=not args.no_backup)
        
        if result['duplicates_removed'] > 0:
            print(f"\n✅ Successfully removed {result['duplicates_removed']} duplicates")
        else:
            print("\n✅ No duplicates found")
            
    except Exception as e:
        print(f"❌ Error during deduplication: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
