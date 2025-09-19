#!/usr/bin/env python3
"""
Merge gallery data from import files into the main gallery.json file.

This script takes gallery-import-*.json files and merges them into the main
gallery.json file, maintaining proper categorization and avoiding duplicates.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
from datetime import datetime

class GalleryMerger:
    def __init__(self, main_gallery_path: str = "assets/data/gallery.json"):
        self.main_gallery_path = Path(main_gallery_path)
        self.main_gallery_data = {}
        self.merged_stats = {
            'total_media': 0,
            'total_duplicates_removed': 0,
            'photos': 0,
            'videos': 0,
            'external_videos': 0,
            'categories_count': 0,
            'years_count': 0,
            'events_count': 0,
            'date_range': {'earliest': None, 'latest': None},
            'credits': {
                'total_credited': 0,
                'total_unknown': 0,
                'unique_credits': 0,
                'top_credits': [],
                'credit_breakdown': {}
            }
        }
    
    def load_main_gallery(self) -> bool:
        """Load the main gallery.json file."""
        if not self.main_gallery_path.exists():
            print(f"Main gallery file not found: {self.main_gallery_path}")
            print("Creating new gallery structure...")
            self.main_gallery_data = {
                'stats': self.merged_stats.copy(),
                'categories': {},
                'years': {},
                'events': {},
                'collections': {},
                'media_index': [],
                'search_terms': {
                    'locations': [],
                    'event_types': [],
                    'years': [],
                    'media_types': [],
                    'platforms': [],
                    'keywords': []
                }
            }
            return True
        
        try:
            with open(self.main_gallery_path, 'r') as f:
                self.main_gallery_data = json.load(f)
            print(f"Loaded main gallery with {self.main_gallery_data.get('stats', {}).get('total_media', 0)} items")
            return True
        except Exception as e:
            print(f"Error loading main gallery: {e}")
            return False
    
    def load_import_files(self, import_pattern: str = "assets/data/gallery-import-*.json") -> List[Dict]:
        """Load all gallery import files matching the pattern."""
        import_files = []
        import_path = Path(import_pattern)
        
        # Find all matching files
        if '*' in str(import_path):
            parent_dir = import_path.parent
            pattern = import_path.name
            matching_files = list(parent_dir.glob(pattern))
        else:
            matching_files = [import_path] if import_path.exists() else []
        
        for file_path in matching_files:
            try:
                with open(file_path, 'r') as f:
                    import_data = json.load(f)
                    import_files.append({
                        'file_path': file_path,
                        'data': import_data
                    })
                    print(f"Loaded import file: {file_path.name}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return import_files
    
    def merge_media_items(self, import_data: Dict) -> List[Dict]:
        """Merge media items from import data, avoiding duplicates."""
        existing_paths = {item['path'] for item in self.main_gallery_data.get('media_index', [])}
        new_items = []
        
        for item in import_data.get('media_index', []):
            if item['path'] not in existing_paths:
                new_items.append(item)
            else:
                print(f"Skipping duplicate: {item['path']}")
        
        return new_items
    
    def merge_categories(self, import_data: Dict, new_items: List[Dict]):
        """Merge categories from import data."""
        import_categories = import_data.get('categories', {})
        
        for category_name, category_items in import_categories.items():
            if category_name not in self.main_gallery_data['categories']:
                self.main_gallery_data['categories'][category_name] = []
            
            # Add new items to this category
            for item in category_items:
                if item in new_items:
                    self.main_gallery_data['categories'][category_name].append(item)
    
    def merge_years(self, import_data: Dict, new_items: List[Dict]):
        """Merge years from import data."""
        import_years = import_data.get('years', {})
        
        for year, year_items in import_years.items():
            if year not in self.main_gallery_data['years']:
                self.main_gallery_data['years'][year] = []
            
            # Add new items to this year
            for item in year_items:
                if item in new_items:
                    self.main_gallery_data['years'][year].append(item)
    
    def merge_events(self, import_data: Dict, new_items: List[Dict]):
        """Merge events from import data."""
        import_events = import_data.get('events', {})
        
        for event_name, event_items in import_events.items():
            if event_name not in self.main_gallery_data['events']:
                self.main_gallery_data['events'][event_name] = []
            
            # Add new items to this event
            for item in event_items:
                if item in new_items:
                    self.main_gallery_data['events'][event_name].append(item)
    
    def merge_collections(self, import_data: Dict, new_items: List[Dict]):
        """Merge collections from import data."""
        import_collections = import_data.get('collections', {})
        
        for collection_name, collection_data in import_collections.items():
            if collection_name not in self.main_gallery_data['collections']:
                self.main_gallery_data['collections'][collection_name] = collection_data
            else:
                # Merge media items
                existing_media = self.main_gallery_data['collections'][collection_name].get('media', [])
                new_media = [item for item in collection_data.get('media', []) if item in new_items]
                self.main_gallery_data['collections'][collection_name]['media'] = existing_media + new_media
    
    def update_stats(self):
        """Update statistics after merging."""
        media_index = self.main_gallery_data.get('media_index', [])
        
        # Count media types
        photos = len([m for m in media_index if m.get('media_type') == 'photo'])
        videos = len([m for m in media_index if m.get('media_type') == 'video'])
        external_videos = len([m for m in media_index if m.get('media_type') == 'external_video'])
        
        # Count years
        years = set()
        for item in media_index:
            if 'year' in item:
                years.add(item['year'])
        
        # Count events
        events = set()
        for item in media_index:
            if 'event' in item and item['event']:
                events.add(item['event'])
        
        # Count credits
        credit_counts = defaultdict(int)
        for item in media_index:
            credit = item.get('credit', 'Unknown photographer')
            credit_counts[credit] += 1
        
        total_credited = sum(1 for credit in credit_counts.keys() if credit != 'Unknown photographer')
        total_unknown = credit_counts.get('Unknown photographer', 0)
        
        # Get date range
        years_list = list(years)
        date_range = {
            'earliest': min(years_list) if years_list else 'unknown',
            'latest': max(years_list) if years_list else 'unknown'
        }
        
        # Update stats
        self.main_gallery_data['stats'] = {
            'total_media': len(media_index),
            'total_duplicates_removed': 0,  # This would need to be tracked separately
            'photos': photos,
            'videos': videos,
            'external_videos': external_videos,
            'categories_count': len(self.main_gallery_data.get('categories', {})),
            'years_count': len(years),
            'events_count': len(events),
            'date_range': date_range,
            'credits': {
                'total_credited': total_credited,
                'total_unknown': total_unknown,
                'unique_credits': len(credit_counts),
                'top_credits': sorted(credit_counts.items(), key=lambda x: x[1], reverse=True)[:10],
                'credit_breakdown': dict(credit_counts)
            }
        }
    
    def merge_import_files(self, import_files: List[Dict]) -> int:
        """Merge all import files into the main gallery."""
        total_new_items = 0
        
        for import_file in import_files:
            print(f"\nMerging {import_file['file_path'].name}...")
            import_data = import_file['data']
            
            # Merge media items
            new_items = self.merge_media_items(import_data)
            total_new_items += len(new_items)
            
            if new_items:
                print(f"  Adding {len(new_items)} new items")
                
                # Add to main media index
                self.main_gallery_data['media_index'].extend(new_items)
                
                # Merge categories, years, events, collections
                self.merge_categories(import_data, new_items)
                self.merge_years(import_data, new_items)
                self.merge_events(import_data, new_items)
                self.merge_collections(import_data, new_items)
            else:
                print("  No new items to add")
        
        # Update statistics
        self.update_stats()
        
        return total_new_items
    
    def save_merged_gallery(self, backup: bool = True) -> bool:
        """Save the merged gallery data."""
        try:
            # Create backup if requested
            if backup and self.main_gallery_path.exists():
                backup_path = self.main_gallery_path.with_name(f'{self.main_gallery_path.stem}.{datetime.now().strftime("%Y%m%d-%H%M%S")}-backup.json')
                self.main_gallery_path.rename(backup_path)
                print(f"Created backup: {backup_path}")
            
            # Save merged data
            with open(self.main_gallery_path, 'w') as f:
                json.dump(self.main_gallery_data, f, indent=2)
            
            print(f"Merged gallery saved to {self.main_gallery_path}")
            return True
        except Exception as e:
            print(f"Error saving merged gallery: {e}")
            return False
    
    def print_summary(self):
        """Print summary of the merged gallery."""
        stats = self.main_gallery_data.get('stats', {})
        print(f"\n📊 Merged Gallery Summary:")
        print(f"Total media: {stats.get('total_media', 0)}")
        print(f"Photos: {stats.get('photos', 0)}")
        print(f"Videos: {stats.get('videos', 0)}")
        print(f"External videos: {stats.get('external_videos', 0)}")
        print(f"Categories: {stats.get('categories_count', 0)}")
        print(f"Years: {stats.get('years_count', 0)}")
        print(f"Events: {stats.get('events_count', 0)}")
        print(f"Date range: {stats.get('date_range', {}).get('earliest', 'unknown')} - {stats.get('date_range', {}).get('latest', 'unknown')}")
        
        credits = stats.get('credits', {})
        print(f"\n📸 Credit Statistics:")
        print(f"Credited media: {credits.get('total_credited', 0)}")
        print(f"Unknown credits: {credits.get('total_unknown', 0)}")
        print(f"Unique credits: {credits.get('unique_credits', 0)}")
        print(f"Top credits:")
        for credit, count in credits.get('top_credits', [])[:5]:
            print(f"  - {credit}: {count} items")

def main():
    parser = argparse.ArgumentParser(description='Merge gallery import files into main gallery.json')
    parser.add_argument('--main-gallery', default='assets/data/gallery.json', 
                       help='Path to main gallery.json file')
    parser.add_argument('--import-pattern', default='assets/data/gallery-import-*.json',
                       help='Pattern for import files to merge')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backup of main gallery file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be merged without making changes')
    
    args = parser.parse_args()
    
    # Create merger
    merger = GalleryMerger(args.main_gallery)
    
    # Load main gallery
    if not merger.load_main_gallery():
        return 1
    
    # Load import files
    import_files = merger.load_import_files(args.import_pattern)
    
    if not import_files:
        print("No import files found to merge.")
        return 0
    
    print(f"\nFound {len(import_files)} import files to merge")
    
    if args.dry_run:
        print("\n🔍 Dry run - showing what would be merged:")
        for import_file in import_files:
            import_data = import_file['data']
            media_count = len(import_data.get('media_index', []))
            print(f"  {import_file['file_path'].name}: {media_count} items")
        return 0
    
    # Merge import files
    total_new_items = merger.merge_import_files(import_files)
    
    if total_new_items > 0:
        # Save merged gallery
        if merger.save_merged_gallery(backup=not args.no_backup):
            merger.print_summary()
            print(f"\n✅ Successfully merged {total_new_items} new items")
        else:
            print("\n❌ Failed to save merged gallery")
            return 1
    else:
        print("\nℹ️ No new items to merge")
    
    return 0

if __name__ == "__main__":
    exit(main())
