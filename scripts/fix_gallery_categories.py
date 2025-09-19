#!/usr/bin/env python3
"""
Fix gallery categories by applying normalization and deduplicating categories.

This script applies normalization to category names and merges duplicate categories
like "BYC" and "Beachwood" into a single normalized category.
"""

import json
import yaml
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class GalleryCategoryFixer:
    def __init__(self, gallery_path: str = "assets/data/gallery.json"):
        self.gallery_path = Path(gallery_path)
        self.backup_path = None
        self.normalization_data = {}
        self.yacht_clubs_data = []
        
        # Load normalization data
        self.load_normalization_data()
    
    def load_normalization_data(self):
        """Load normalization and yacht clubs data."""
        # Load normalization data
        norm_path = Path("_data/normalization.yml")
        if norm_path.exists():
            try:
                with open(norm_path, 'r', encoding='utf-8') as f:
                    self.normalization_data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Error loading normalization data: {e}")
                self.normalization_data = {}
        else:
            print("Warning: No normalization data file found at _data/normalization.yml")
            self.normalization_data = {}
        
        # Load yacht clubs data
        yachtclubs_path = Path("_data/yachtclubs.yml")
        if yachtclubs_path.exists():
            try:
                with open(yachtclubs_path, 'r', encoding='utf-8') as f:
                    self.yacht_clubs_data = yaml.safe_load(f) or []
            except Exception as e:
                print(f"Error loading yacht clubs data: {e}")
                self.yacht_clubs_data = []
        else:
            print("Warning: No yacht clubs data file found at _data/yachtclubs.yml")
            self.yacht_clubs_data = []
    
    def normalize_category_name(self, category: str) -> str:
        """Normalize category name using club aliases and yacht club full names."""
        if not category:
            return category
        
        # Check club aliases first
        club_aliases = self.normalization_data.get('club_aliases', {})
        if category in club_aliases:
            return club_aliases[category]
        
        # Check yacht clubs data for abbreviations
        for club in self.yacht_clubs_data:
            if isinstance(club, dict):
                name = club.get('name', '')
                # Check if the category matches an abbreviation in the club name
                if category.upper() in name.upper() or name.upper() in category.upper():
                    return name
        
        return category
    
    def create_backup(self):
        """Create a backup of the gallery file before fixing."""
        if self.gallery_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.backup_path = self.gallery_path.with_name(f'{self.gallery_path.stem}.{timestamp}-backup.json')
            self.gallery_path.rename(self.backup_path)
            print(f"Created backup: {self.backup_path}")
            return True
        return False
    
    def fix_categories(self, create_backup: bool = True) -> dict:
        """Fix categories by applying normalization and deduplicating."""
        if create_backup:
            self.create_backup()
        
        # Load gallery data from backup if it exists, otherwise from original
        source_path = self.backup_path if self.backup_path else self.gallery_path
        if not source_path.exists():
            raise FileNotFoundError(f"Gallery file not found: {source_path}")
        
        with open(source_path, 'r', encoding='utf-8') as f:
            gallery_data = json.load(f)
        
        # Track category mappings and changes
        category_mappings = {}
        changes_made = []
        
        # Process each media item
        for item in gallery_data.get('media_index', []):
            original_categories = item.get('categories', [])
            normalized_categories = []
            
            for category in original_categories:
                normalized_category = self.normalize_category_name(category)
                if normalized_category != category:
                    category_mappings[category] = normalized_category
                    changes_made.append(f"{category} -> {normalized_category}")
                
                if normalized_category not in normalized_categories:
                    normalized_categories.append(normalized_category)
            
            item['categories'] = normalized_categories
        
        # Also process the categories index
        original_categories = gallery_data.get('categories', {})
        for category_name in list(original_categories.keys()):
            normalized_name = self.normalize_category_name(category_name)
            if normalized_name != category_name:
                category_mappings[category_name] = normalized_name
                changes_made.append(f"{category_name} -> {normalized_name}")
        
        # Rebuild categories index with normalized names
        new_categories = defaultdict(list)
        for item in gallery_data.get('media_index', []):
            for category in item.get('categories', []):
                new_categories[category].append(item)
        
        # Update gallery data
        gallery_data['categories'] = dict(new_categories)
        
        # Also rebuild years and events indexes
        new_years = defaultdict(list)
        new_events = defaultdict(list)
        for item in gallery_data.get('media_index', []):
            year = item.get('year')
            if year:
                new_years[year].append(item)
            event = item.get('event')
            if event:
                new_events[event].append(item)
        
        gallery_data['years'] = dict(new_years)
        gallery_data['events'] = dict(new_events)
        
        # Update statistics
        gallery_data['stats']['categories_count'] = len(new_categories)
        
        # Save fixed data
        with open(self.gallery_path, 'w', encoding='utf-8') as f:
            json.dump(gallery_data, f, indent=2, ensure_ascii=False)
        
        print(f"Category fixing complete:")
        print(f"  Categories before: {len(gallery_data.get('categories', {}))}")
        print(f"  Categories after: {len(new_categories)}")
        print(f"  Category mappings made: {len(category_mappings)}")
        print(f"  Saved to: {self.gallery_path}")
        
        if changes_made:
            print("\nCategory changes made:")
            for change in set(changes_made):
                print(f"  {change}")
        
        return {
            'categories_before': len(gallery_data.get('categories', {})),
            'categories_after': len(new_categories),
            'mappings_made': len(category_mappings),
            'changes': list(set(changes_made)),
            'backup_path': str(self.backup_path) if self.backup_path else None
        }

def main():
    parser = argparse.ArgumentParser(description='Fix gallery categories with normalization')
    parser.add_argument('--gallery-path', default='assets/data/gallery.json',
                       help='Path to gallery.json file')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backup before fixing')
    
    args = parser.parse_args()
    
    fixer = GalleryCategoryFixer(args.gallery_path)
    
    try:
        result = fixer.fix_categories(create_backup=not args.no_backup)
        
        if result['mappings_made'] > 0:
            print(f"\n✅ Successfully fixed {result['mappings_made']} category mappings")
        else:
            print("\n✅ No category changes needed")
            
    except Exception as e:
        print(f"❌ Error during category fixing: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
