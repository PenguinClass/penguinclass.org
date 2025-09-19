#!/usr/bin/env python3
"""
Import gallery data for a specific directory with custom metadata.

This script creates gallery data for a specific directory with configurable
metadata like date, source, credit, etc.
"""

import json
import re
import subprocess
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict
from urllib.parse import urlparse, quote
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent))
from lib.gallery_utils import GalleryUtils

# Photo extensions to look for
PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}

# Video extensions to look for
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v'}

class GalleryImporter:
    def __init__(self, import_path: str, date: str = None, source: str = None, 
                 credit: str = None, event: str = None, location: str = None):
        self.import_path = Path(import_path)
        self.date = date
        self.source = source or "import"
        self.credit = credit or "Unknown photographer"
        self.event = event
        self.location = location
        self.media_items = []
        self.categories = defaultdict(list)
        self.events = defaultdict(list)
        self.years = defaultdict(list)
        self.utils = GalleryUtils()
    
    def load_normalization_data(self):
        """Load normalization and yacht clubs data."""
        # Load normalization data
        norm_path = Path("_data/normalization.yml")
        if norm_path.exists():
            try:
                with open(norm_path, 'r') as f:
                    self.normalization_data = yaml.safe_load(f) or {}
                print(f"Loaded normalization data")
            except Exception as e:
                print(f"Error loading normalization data: {e}")
                self.normalization_data = {}
        
        # Load yacht clubs data
        clubs_path = Path("_data/yachtclubs.yml")
        if clubs_path.exists():
            try:
                with open(clubs_path, 'r') as f:
                    self.yacht_clubs_data = yaml.safe_load(f) or []
                print(f"Loaded {len(self.yacht_clubs_data)} yacht clubs")
            except Exception as e:
                print(f"Error loading yacht clubs data: {e}")
                self.yacht_clubs_data = []
    
    def normalize_category_name(self, category: str) -> str:
        """Normalize category name using club aliases and yacht clubs data."""
        # Check club aliases first
        club_aliases = self.normalization_data.get('club_aliases', {})
        if category in club_aliases:
            return club_aliases[category]
        
        # Check yacht clubs data for full names
        for club in self.yacht_clubs_data:
            if club.get('name') == category:
                return category
            # Check if category is an abbreviation of the club name
            club_words = club.get('name', '').split()
            if len(club_words) > 1:
                abbreviation = ''.join(word[0] for word in club_words)
                if abbreviation == category:
                    return club.get('name', category)
        
        return category
    
    def extract_exif_metadata(self, file_path: str) -> Dict:
        """Extract only useful EXIF metadata from image file using exiftool."""
        exif_data = {}
        
        # Define the useful EXIF fields we want to keep
        useful_fields = [
            'DateTime', 'DateTimeOriginal', 'CreateDate', 'ModifyDate',
            'GPSLatitude', 'GPSLongitude', 'GPSAltitude', 'GPSLocation',
            'Artist', 'Copyright', 'ImageDescription', 'UserComment',
            'ImageWidth', 'ImageHeight', 'ExifImageWidth', 'ExifImageHeight',
            'Make', 'Model', 'Software', 'LensModel'
        ]
        
        try:
            # Try exiftool with specific field selection
            field_args = []
            for field in useful_fields:
                field_args.extend(['-{}'.format(field)])
            
            result = subprocess.run(['exiftool', '-json', '-q'] + field_args + [file_path], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                exif_json = json.loads(result.stdout)
                if exif_json and len(exif_json) > 0:
                    raw_exif = exif_json[0]
                    # Filter to only include useful fields
                    exif_data = {k: v for k, v in raw_exif.items() if k in useful_fields}
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            # Fallback to file command for basic info
            try:
                result = subprocess.run(['file', file_path], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    file_output = result.stdout
                    # Extract basic info from file output
                    if 'Exif Standard' in file_output:
                        # Parse manufacturer, model, datetime from file output
                        if 'manufacturer=' in file_output:
                            manufacturer = re.search(r'manufacturer=([^,]+)', file_output)
                            if manufacturer:
                                exif_data['Make'] = manufacturer.group(1).strip()
                        if 'model=' in file_output:
                            model = re.search(r'model=([^,]+)', file_output)
                            if model:
                                exif_data['Model'] = model.group(1).strip()
                        if 'datetime=' in file_output:
                            datetime_match = re.search(r'datetime=([^,]+)', file_output)
                            if datetime_match:
                                exif_data['DateTime'] = datetime_match.group(1).strip()
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                pass
        
        return exif_data
    
    def url_encode_path(self, path: str) -> str:
        """URL encode special characters in file paths."""
        # Split the path into directory and filename parts
        path_obj = Path(path)
        encoded_parts = []
        
        # Encode each part of the path
        for part in path_obj.parts:
            # Only encode special characters that cause issues in URLs
            encoded_part = quote(part, safe='')
            encoded_parts.append(encoded_part)
        
        return '/'.join(encoded_parts)
    
    def get_media_type(self, file_path: str) -> str:
        """Determine if this is a photo or video."""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension in PHOTO_EXTENSIONS:
            return 'photo'
        elif extension in VIDEO_EXTENSIONS:
            return 'video'
        else:
            return 'unknown'
    
    def extract_metadata(self, file_path: str, file_size: int = 0, modified_time: str = '') -> Dict:
        """Extract metadata from media file."""
        media_type = self.get_media_type(file_path)
        filename = Path(file_path).name
        
        # Extract EXIF data for images
        exif_data = {}
        if media_type == 'photo' and Path(file_path).suffix.lower() in {'.jpg', '.jpeg', '.tiff', '.tif'}:
            exif_data = self.extract_exif_metadata(file_path)
        
        # Extract year from date parameter or filename
        year = None
        if self.date:
            try:
                year = int(self.date.split('-')[0])
            except (ValueError, IndexError):
                pass
        
        if not year:
            year_match = re.search(r'\b(19|20)\d{2}\b', file_path)
            if year_match:
                year = int(year_match.group())
        
        metadata = {
            'filename': filename,
            'path': file_path,
            'encoded_path': self.url_encode_path(file_path),
            'size': file_size,
            'modified': modified_time,
            'extension': Path(file_path).suffix.lower(),
            'media_type': media_type,
            'source': self.source,
            'credit': self.credit,
            'date': self.date,
            'event': self.event,
            'location': self.location,
            'caption': '',  # Add caption field for future use
            'exif': exif_data
        }
        
        if year:
            metadata['year'] = year
        
        return metadata
    
    def categorize_media(self, metadata: Dict) -> List[str]:
        """Categorize media based on metadata and filename."""
        categories = []
        filename = metadata['filename'].lower()
        path = metadata['path'].lower()
        
        # Media type categories
        if metadata['media_type'] == 'video':
            categories.append('Videos')
        elif metadata['media_type'] == 'photo':
            categories.append('Photos')
        
        # Event-based categories
        if self.event:
            if 'championship' in self.event.lower() or 'champ' in self.event.lower():
                categories.append('Championships')
            elif 'regatta' in self.event.lower():
                categories.append('Regattas')
            elif 'frostbite' in self.event.lower():
                categories.append('Frostbite')
            elif 'heritage' in self.event.lower():
                categories.append('Heritage')
        
        # Location-based categories (normalized)
        if self.location:
            normalized_location = self.normalize_category_name(self.location)
            categories.append(normalized_location)
        
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
    
    def organize_media(self, media_list: List[Dict]):
        """Organize media by categories, events, and years."""
        for media in media_list:
            # Add to year-based organization
            if 'year' in media:
                self.years[media['year']].append(media)
            
            # Add to event-based organization
            if self.event:
                self.events[self.event].append(media)
            
            # Add to category-based organization
            categories = self.categorize_media(media)
            for category in categories:
                self.categories[category].append(media)
    
    def scan_directory(self) -> List[Dict]:
        """Scan the import directory for media files."""
        media_files = []
        
        if not self.import_path.exists():
            print(f"Error: Import path does not exist: {self.import_path}")
            return media_files
        
        print(f"Scanning directory: {self.import_path}")
        
        # Find all media files
        for file_path in self.import_path.rglob('*'):
            if file_path.is_file():
                extension = file_path.suffix.lower()
                if extension in PHOTO_EXTENSIONS or extension in VIDEO_EXTENSIONS:
                    # Get file stats
                    stat = file_path.stat()
                    file_size = stat.st_size
                    modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    
                    # Create relative path from project root
                    try:
                        relative_path = file_path.relative_to(Path.cwd())
                    except ValueError:
                        relative_path = file_path
                    
                    media_files.append({
                        'path': str(relative_path),
                        'size': file_size,
                        'modified': modified_time
                    })
        
        print(f"Found {len(media_files)} media files")
        return media_files
    
    def generate_gallery_data(self) -> Dict:
        """Generate structured data for the gallery."""
        # Scan directory for media files
        media_files = self.scan_directory()
        
        if not media_files:
            print("No media files found in the import directory.")
            return {}
        
        # Convert to media items with enhanced metadata
        media_items = []
        for media_file in media_files:
            media_metadata = self.extract_metadata(
                media_file['path'], 
                media_file.get('size', 0), 
                media_file.get('modified', '')
            )
            media_items.append(media_metadata)
        
        # Organize media
        self.organize_media(media_items)
        
        # Create summary statistics
        stats = {
            'total_media': len(media_items),
            'photos': len([m for m in media_items if m['media_type'] == 'photo']),
            'videos': len([m for m in media_items if m['media_type'] == 'video']),
            'categories_count': len(self.categories),
            'years_count': len(self.years),
            'events_count': len(self.events),
            'date_range': {
                'earliest': min(self.years.keys()) if self.years else 'unknown',
                'latest': max(self.years.keys()) if self.years else 'unknown'
            },
            'import_info': {
                'date': self.date,
                'source': self.source,
                'credit': self.credit,
                'event': self.event,
                'location': self.location,
                'import_path': str(self.import_path)
            }
        }
        
        # Create gallery collections
        collections = {
            'imported': {
                'title': f'Imported from {self.import_path.name}',
                'description': f'Media imported on {datetime.now().strftime("%Y-%m-%d")}',
                'media': media_items
            }
        }
        
        if self.event:
            collections['event'] = {
                'title': self.event,
                'description': f'Media from {self.event}',
                'media': media_items
            }
        
        return {
            'stats': stats,
            'categories': dict(self.categories),
            'years': dict(self.years),
            'events': dict(self.events),
            'collections': collections,
            'media_index': media_items,
            'search_terms': self.generate_search_terms(media_items)
        }
    
    def generate_search_terms(self, media_items: List[Dict]) -> Dict[str, List[str]]:
        """Generate search terms for the media gallery."""
        terms = {
            'locations': set(),
            'event_types': set(),
            'years': set(),
            'media_types': set(),
            'keywords': set()
        }
        
        for media in media_items:
            if media.get('location') and media['location'] != 'unknown':
                terms['locations'].add(media['location'])
            if media.get('event') and media['event'] != 'general':
                terms['event_types'].add(media['event'])
            if media.get('year'):
                terms['years'].add(str(media['year']))
            if media.get('media_type'):
                terms['media_types'].add(media['media_type'])
            
            # Extract keywords from filename
            filename_words = re.findall(r'\b[a-zA-Z]+\b', media['filename'].lower())
            terms['keywords'].update(filename_words)
        
        # Convert sets to sorted lists
        return {k: sorted(list(v)) for k, v in terms.items()}
    
    def save_gallery_data(self, output_file: str = None, merge_to_main: bool = False):
        """Save the gallery data to a JSON file or merge into main gallery."""
        gallery_data = self.generate_gallery_data()
        
        if not gallery_data:
            print("No data to save.")
            return
        
        if merge_to_main:
            # Merge directly into main gallery
            self.merge_to_main_gallery(gallery_data)
        else:
            # Save as separate import file
            if not output_file:
                output_file = f"assets/data/gallery-import-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            
            output_path = Path(output_file)
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(gallery_data, f, indent=2)
            
            print(f"Gallery data saved to {output_path}")
        
        # Print summary
        stats = gallery_data['stats']
        print(f"\n📊 Import Summary:")
        print(f"Total media: {stats['total_media']}")
        print(f"Photos: {stats['photos']}")
        print(f"Videos: {stats['videos']}")
        print(f"Categories: {stats['categories_count']}")
        print(f"Years: {stats['years_count']}")
        print(f"Events: {stats['events_count']}")
        print(f"Date range: {stats['date_range']['earliest']} - {stats['date_range']['latest']}")
        
        import_info = stats['import_info']
        print(f"\n📁 Import Information:")
        print(f"Date: {import_info['date']}")
        print(f"Source: {import_info['source']}")
        print(f"Credit: {import_info['credit']}")
        print(f"Event: {import_info['event']}")
        print(f"Location: {import_info['location']}")
        print(f"Path: {import_info['import_path']}")
        
        # Print collection summaries
        print(f"\n📁 Collections:")
        for name, collection in gallery_data['collections'].items():
            print(f"  {collection['title']}: {len(collection['media'])} items")
    
    def merge_to_main_gallery(self, gallery_data: Dict):
        """Merge this gallery data directly into the main gallery.json file."""
        main_gallery_path = Path("assets/data/gallery.json")
        
        # Load existing main gallery or create new structure
        if main_gallery_path.exists():
            try:
                with open(main_gallery_path, 'r') as f:
                    main_gallery = json.load(f)
                print(f"Loaded existing main gallery with {main_gallery.get('stats', {}).get('total_media', 0)} items")
            except Exception as e:
                print(f"Error loading main gallery: {e}")
                return
        else:
            print("Creating new main gallery structure")
            main_gallery = {
                'stats': {
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
                },
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
        
        # Get existing paths to avoid duplicates
        existing_paths = {item['path'] for item in main_gallery.get('media_index', [])}
        
        # Add new items
        new_items = []
        for item in gallery_data.get('media_index', []):
            if item['path'] not in existing_paths:
                new_items.append(item)
            else:
                print(f"Skipping duplicate: {item['path']}")
        
        if not new_items:
            print("No new items to add to main gallery")
            return
        
        # Add to main gallery
        main_gallery['media_index'].extend(new_items)
        
        # Merge categories
        for category_name, category_items in gallery_data.get('categories', {}).items():
            if category_name not in main_gallery['categories']:
                main_gallery['categories'][category_name] = []
            main_gallery['categories'][category_name].extend([item for item in category_items if item in new_items])
        
        # Merge years
        for year, year_items in gallery_data.get('years', {}).items():
            if year not in main_gallery['years']:
                main_gallery['years'][year] = []
            main_gallery['years'][year].extend([item for item in year_items if item in new_items])
        
        # Merge events
        for event_name, event_items in gallery_data.get('events', {}).items():
            if event_name not in main_gallery['events']:
                main_gallery['events'][event_name] = []
            main_gallery['events'][event_name].extend([item for item in event_items if item in new_items])
        
        # Merge collections
        for collection_name, collection_data in gallery_data.get('collections', {}).items():
            if collection_name not in main_gallery['collections']:
                main_gallery['collections'][collection_name] = collection_data
            else:
                existing_media = main_gallery['collections'][collection_name].get('media', [])
                new_media = [item for item in collection_data.get('media', []) if item in new_items]
                main_gallery['collections'][collection_name]['media'] = existing_media + new_media
        
        # Update statistics
        media_index = main_gallery['media_index']
        photos = len([m for m in media_index if m.get('media_type') == 'photo'])
        videos = len([m for m in media_index if m.get('media_type') == 'video'])
        external_videos = len([m for m in media_index if m.get('media_type') == 'external_video'])
        
        years = set()
        for item in media_index:
            if 'year' in item:
                years.add(item['year'])
        
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
        
        # Update stats
        main_gallery['stats'] = {
            'total_media': len(media_index),
            'total_duplicates_removed': main_gallery['stats'].get('total_duplicates_removed', 0),
            'photos': photos,
            'videos': videos,
            'external_videos': external_videos,
            'categories_count': len(main_gallery.get('categories', {})),
            'years_count': len(years),
            'events_count': len(events),
            'date_range': {
                'earliest': min(years) if years else 'unknown',
                'latest': max(years) if years else 'unknown'
            },
            'credits': {
                'total_credited': total_credited,
                'total_unknown': total_unknown,
                'unique_credits': len(credit_counts),
                'top_credits': sorted(credit_counts.items(), key=lambda x: x[1], reverse=True)[:10],
                'credit_breakdown': dict(credit_counts)
            }
        }
        
        # Create backup
        if main_gallery_path.exists():
            backup_path = main_gallery_path.with_name(f'{main_gallery_path.stem}.{datetime.now().strftime("%Y%m%d-%H%M%S")}-backup.json')
            main_gallery_path.rename(backup_path)
            print(f"Created backup: {backup_path}")
        
        # Save merged gallery
        main_gallery_path.parent.mkdir(exist_ok=True)
        with open(main_gallery_path, 'w') as f:
            json.dump(main_gallery, f, indent=2)
        
        print(f"✅ Merged {len(new_items)} new items into main gallery: {main_gallery_path}")
        print(f"📊 Main gallery now has {len(media_index)} total items")

def main():
    parser = argparse.ArgumentParser(description='Import gallery data for a specific directory')
    parser.add_argument('import_path', help='Path to directory containing media files')
    parser.add_argument('--date', help='Date of the event (YYYY-MM-DD format)')
    parser.add_argument('--source', default='import', help='Source of the media (default: import)')
    parser.add_argument('--credit', help='Photographer/videographer credit')
    parser.add_argument('--event', help='Event name')
    parser.add_argument('--location', help='Event location')
    parser.add_argument('--output', help='Output JSON file path')
    parser.add_argument('--merge', action='store_true', 
                       help='Merge directly into main gallery.json instead of creating separate import file')
    
    args = parser.parse_args()
    
    # Create importer
    importer = GalleryImporter(
        import_path=args.import_path,
        date=args.date,
        source=args.source,
        credit=args.credit,
        event=args.event,
        location=args.location
    )
    
    # Save gallery data
    importer.save_gallery_data(args.output, merge_to_main=args.merge)

if __name__ == "__main__":
    main()
