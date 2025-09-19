#!/usr/bin/env python3
"""
Fix gallery categories and normalize photographer credits.

This script:
1. Populates categories from filenames, paths, and event keywords
2. Normalizes photographer names (handles underscores, capitalization)
3. Rebuilds the categories index
"""

import json
import re
import yaml
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class GalleryCategoryAndCreditFixer:
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
        
        # Load yacht clubs data
        yachtclubs_path = Path("_data/yachtclubs.yml")
        if yachtclubs_path.exists():
            try:
                with open(yachtclubs_path, 'r', encoding='utf-8') as f:
                    self.yacht_clubs_data = yaml.safe_load(f) or []
            except Exception as e:
                print(f"Error loading yacht clubs data: {e}")
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
    
    def normalize_photographer_name(self, name: str) -> str:
        """Normalize photographer name by handling underscores and capitalization."""
        if not name or name.lower() in ['unknown photographer', 'unknown', '']:
            return 'Unknown photographer'
        
        # Replace underscores with spaces
        normalized = name.replace('_', ' ')
        
        # Handle common variations
        normalized = re.sub(r'\s+', ' ', normalized)  # Multiple spaces to single space
        normalized = normalized.strip()
        
        # Title case but preserve some exceptions
        words = normalized.split()
        result = []
        for word in words:
            if word.upper() in ['MD', 'NJ', 'NY', 'CA', 'USA', 'U.S.A.']:
                result.append(word.upper())
            elif word.lower() in ['of', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with', 'by']:
                result.append(word.lower())
            else:
                result.append(word.title())
        
        return ' '.join(result)
    
    def extract_categories_from_metadata(self, item: dict) -> list:
        """Extract categories from filename, path, and other metadata."""
        categories = []
        filename = item.get('filename', '').lower()
        path = item.get('path', '').lower()
        event_keyword = item.get('event_keyword', '').lower()
        media_type = item.get('media_type', '')
        
        # Media type categories
        if media_type == 'video':
            categories.append('Videos')
        elif media_type == 'photo':
            categories.append('Photos')
        
        # Event-based categories
        if any(word in filename or word in path or word in event_keyword for word in ['international', 'champ']):
            categories.append('Championships')
        elif any(word in filename or word in path or word in event_keyword for word in ['annual', 'regatta']):
            categories.append('Regattas')
        elif any(word in filename or word in path or word in event_keyword for word in ['frostbite']):
            categories.append('Frostbite')
        elif any(word in filename or word in path or word in event_keyword for word in ['heritage']):
            categories.append('Heritage')
        
        # Location-based categories (normalized)
        if any(word in filename or word in path or word in event_keyword for word in ['tayc', 'tred avon']):
            categories.append(self.normalize_category_name('TAYC'))
        elif any(word in filename or word in path or word in event_keyword for word in ['cryc', 'corsica']):
            categories.append(self.normalize_category_name('CRYC'))
        elif any(word in filename or word in path or word in event_keyword for word in ['giys', 'greenwich']):
            categories.append(self.normalize_category_name('GIYS'))
        elif any(word in filename or word in path or word in event_keyword for word in ['beachwood', 'byc', 'baltimore']):
            categories.append(self.normalize_category_name('BYC'))
        
        # Type-based categories
        if any(word in filename or word in path or word in event_keyword for word in ['boat', 'sail', 'rigging']):
            categories.append('Boats')
        elif any(word in filename or word in path or word in event_keyword for word in ['people', 'crew', 'sailor']):
            categories.append('People')
        elif any(word in filename or word in path or word in event_keyword for word in ['award', 'trophy', 'prize']):
            categories.append('Awards')
        
        # Remove duplicates and return
        return list(set(categories))
    
    def create_backup(self):
        """Create a backup of the gallery file before fixing."""
        if self.gallery_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.backup_path = self.gallery_path.with_name(f'{self.gallery_path.stem}.{timestamp}-backup.json')
            self.gallery_path.rename(self.backup_path)
            print(f"Created backup: {self.backup_path}")
            return True
        return False
    
    def fix_categories_and_credits(self, create_backup: bool = True) -> dict:
        """Fix categories and normalize photographer credits."""
        if create_backup:
            self.create_backup()
        
        # Load gallery data from backup if it exists, otherwise from original
        source_path = self.backup_path if self.backup_path else self.gallery_path
        if not source_path.exists():
            raise FileNotFoundError(f"Gallery file not found: {source_path}")
        
        with open(source_path, 'r', encoding='utf-8') as f:
            gallery_data = json.load(f)
        
        # Track changes
        categories_added = 0
        credits_normalized = 0
        
        # Process each media item
        for item in gallery_data.get('media_index', []):
            # Normalize photographer credit
            original_credit = item.get('credit', '')
            normalized_credit = self.normalize_photographer_name(original_credit)
            if normalized_credit != original_credit:
                item['credit'] = normalized_credit
                credits_normalized += 1
            
            # Extract and populate categories
            categories = self.extract_categories_from_metadata(item)
            if categories:
                item['categories'] = categories
                categories_added += 1
        
        # Rebuild categories index
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
        gallery_data['stats']['years_count'] = len(new_years)
        gallery_data['stats']['events_count'] = len(new_events)
        
        # Save fixed data
        with open(self.gallery_path, 'w', encoding='utf-8') as f:
            json.dump(gallery_data, f, indent=2, ensure_ascii=False)
        
        print(f"Category and credit fixing complete:")
        print(f"  Categories populated for {categories_added} items")
        print(f"  Credits normalized for {credits_normalized} items")
        print(f"  Total categories: {len(new_categories)}")
        print(f"  Saved to: {self.gallery_path}")
        
        return {
            'categories_added': categories_added,
            'credits_normalized': credits_normalized,
            'total_categories': len(new_categories),
            'backup_path': str(self.backup_path) if self.backup_path else None
        }

def main():
    parser = argparse.ArgumentParser(description='Fix gallery categories and normalize photographer credits')
    parser.add_argument('--gallery-path', default='assets/data/gallery.json',
                       help='Path to gallery.json file')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backup before fixing')
    
    args = parser.parse_args()
    
    fixer = GalleryCategoryAndCreditFixer(args.gallery_path)
    
    try:
        result = fixer.fix_categories_and_credits(create_backup=not args.no_backup)
        
        print(f"\n✅ Successfully processed gallery data")
        print(f"   Categories added: {result['categories_added']}")
        print(f"   Credits normalized: {result['credits_normalized']}")
        print(f"   Total categories: {result['total_categories']}")
            
    except Exception as e:
        print(f"❌ Error during fixing: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
