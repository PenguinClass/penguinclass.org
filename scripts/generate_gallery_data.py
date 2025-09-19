#!/usr/bin/env python3
"""
Generate structured gallery data for the photo and video gallery system.

This script creates a comprehensive JSON file with all media metadata
organized for easy browsing and searching.
"""

import json
import re
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict
from urllib.parse import urlparse, quote
import sys
sys.path.append(str(Path(__file__).parent))
from lib.gallery_utils import GalleryUtils

# Photo extensions to look for
PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}

# Video extensions to look for
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v'}

# External video platforms
EXTERNAL_VIDEO_PLATFORMS = {
    'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com', 'twitch.tv'
}

# Directories to exclude
EXCLUDED_DIRECTORIES = {
    'Penguin_web_dec2010',
    '_vti_cnf'
}

# Directories to analyze
ARCHIVE_DIR = Path("archive/legacy-website")
JEKYLL_DIR = Path("pages/gallery")
ASSETS_DIR = Path("assets/images")

class MediaAnalyzer:
    def __init__(self):
        self.media_items = []
        self.categories = defaultdict(list)
        self.events = defaultdict(list)
        self.years = defaultdict(list)
        self.exclusion_rules = self.load_exclusion_rules()
        self.credit_overrides = self.load_credit_overrides()
        self.utils = GalleryUtils()
    
    
    def load_exclusion_rules(self) -> Dict:
        """Load exclusion rules from the JSON file."""
        exclusion_file = Path("assets/data/gallery-exclude.json")
        if not exclusion_file.exists():
            print("Warning: No exclusion rules file found at assets/data/gallery-exclude.json")
            return {
                'exclude_paths': [],
                'exclude_regex_patterns': [],
                'exclude_urls': [],
                'size_limits': {'min_size_kb': 0, 'max_size_kb': None}
            }
        
        try:
            with open(exclusion_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading exclusion rules: {e}")
            return {
                'exclude_paths': [],
                'exclude_regex_patterns': [],
                'exclude_urls': [],
                'size_limits': {'min_size_kb': 0, 'max_size_kb': None}
            }
    
    def load_credit_overrides(self) -> Dict:
        """Load manual credit overrides from JSON file."""
        credit_file = Path("assets/data/gallery-credits.json")
        if not credit_file.exists():
            print("Info: No credit overrides file found at assets/data/gallery-credits.json")
            return {}
        
        try:
            with open(credit_file, 'r') as f:
                data = json.load(f)
                return data.get('overrides', {})
        except Exception as e:
            print(f"Error loading credit overrides: {e}")
            return {}
    
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
    
    def is_excluded_path(self, path: Path) -> bool:
        """Check if path should be excluded based on exclusion rules."""
        path_str = str(path)
        
        # Check for excluded directories (legacy hardcoded exclusions)
        for excluded_dir in EXCLUDED_DIRECTORIES:
            if f'/{excluded_dir}/' in path_str or path_str.endswith(f'/{excluded_dir}'):
                return True
        
        # Check explicit path exclusions
        for exclude_path in self.exclusion_rules.get('exclude_paths', []):
            if path_str == exclude_path or path_str.endswith(exclude_path):
                return True
        
        # Check regex pattern exclusions
        for pattern_info in self.exclusion_rules.get('exclude_regex_patterns', []):
            pattern = pattern_info.get('pattern', '')
            try:
                if re.search(pattern, path_str):
                    return True
            except re.error as e:
                print(f"Warning: Invalid regex pattern '{pattern}': {e}")
        
        return False
    
    def is_excluded_by_size(self, file_size: int) -> bool:
        """Check if file should be excluded based on size limits."""
        size_limits = self.exclusion_rules.get('size_limits', {})
        min_size_kb = size_limits.get('min_size_kb', 0)
        max_size_kb = size_limits.get('max_size_kb')
        
        # Convert bytes to KB
        size_kb = file_size / 1024
        
        if min_size_kb and size_kb < min_size_kb:
            return True
        
        if max_size_kb and size_kb > max_size_kb:
            return True
        
        return False
    
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

    def extract_credit_from_metadata(self, filename: str, path: str, exif_data: Dict = None) -> str:
        """Extract photographer/videographer credit using multiple methods."""
        filename_lower = filename.lower()
        path_lower = path.lower()
        
        # 1. Check for manual overrides first
        if path in self.credit_overrides:
            return self.utils.normalize_photographer_name(self.credit_overrides[path])
        
        # 2. Check for explicit photographer patterns in filename (conservative approach)
        photographer_patterns = [
            r'_by_([a-zA-Z_]+)',  # _by_John or _by_John_Smith
            r'photoby([a-zA-Z_]+)',  # photobyJohn or photobyJohn_Smith
            r'photo_by_([a-zA-Z_]+)',  # photo_by_John or photo_by_John_Smith
            r'credit_([a-zA-Z_]+)',  # credit_John or credit_John_Smith
        ]
        
        for pattern in photographer_patterns:
            match = re.search(pattern, filename_lower)
            if match:
                name = match.group(1)
                normalized_name = self.utils.normalize_photographer_name(name)
                return f"Photo by {normalized_name}"
        
        # 3. Check for copyright notices in filename
        if 'copyright' in filename_lower or '©' in filename:
            return "Copyright protected"
        
        # 4. Check for watermarks or credits in filename
        if 'watermark' in filename_lower or 'credit' in filename_lower:
            return "Credited photographer"
        
        # 5. Use EXIF data if available
        if exif_data:
            # Check for photographer in EXIF
            if 'Artist' in exif_data and exif_data['Artist'].strip():
                return f"Photo by {self.utils.normalize_photographer_name(exif_data['Artist'].strip())}"
            if 'Copyright' in exif_data and exif_data['Copyright'].strip():
                return self.utils.normalize_photographer_name(exif_data['Copyright'].strip())
            if 'Creator' in exif_data and exif_data['Creator'].strip():
                return f"Photo by {self.utils.normalize_photographer_name(exif_data['Creator'].strip())}"
        
        # 6. Check for known photographer directories (conservative)
        known_photographer_dirs = {
            'will', 'keyworth', 'frank', 'parisi'
        }
        
        for photographer in known_photographer_dirs:
            if f'/{photographer}/' in path_lower or path_lower.endswith(f'/{photographer}'):
                return f"Photo by {self.utils.normalize_photographer_name(photographer)}"
        
        # Default for unknown
        return "Unknown photographer"
    
    def is_external_url(self, url: str) -> bool:
        """Check if URL is external."""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc)
        except:
            return False
    
    def get_media_type(self, file_path: str) -> str:
        """Determine if this is a photo, video, or external media."""
        if self.is_external_url(file_path):
            # Check if it's an external video platform
            parsed = urlparse(file_path)
            if any(platform in parsed.netloc for platform in EXTERNAL_VIDEO_PLATFORMS):
                return 'external_video'
            else:
                return 'external_media'
        
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
            exif_data = self.utils.extract_exif_metadata(file_path)
        
        metadata = {
            'filename': filename,
            'path': file_path,
            'encoded_path': self.utils.url_encode_path(file_path),
            'size': file_size,
            'modified': modified_time,
            'extension': Path(file_path).suffix.lower(),
            'media_type': media_type,
            'source': 'archive' if 'archive' in file_path else 'jekyll',
            'credit': self.extract_credit_from_metadata(filename, file_path, exif_data),
            'exif': exif_data
        }
        
        # Handle external URLs
        if self.is_external_url(file_path):
            metadata['is_external'] = True
            metadata['external_url'] = file_path
            metadata['external_platform'] = self.get_external_platform(file_path)
        else:
            metadata['is_external'] = False
        
        # Try to extract year from filename or path
        year_match = re.search(r'\b(19|20)\d{2}\b', file_path)
        if year_match:
            metadata['year'] = int(year_match.group())
        
        # Try to extract event information
        filename_lower = file_path.lower()
        
        # Common event keywords
        event_keywords = [
            'international', 'championship', 'champ', 'north american', 'na',
            'annual', 'regatta', 'frostbite', 'heritage', 'turkey trot',
            'spring', 'summer', 'fall', 'winter', 'tayc', 'cryc', 'giys',
            'beachwood', 'corsica', 'admiral byrd', 'meyers'
        ]
        
        for keyword in event_keywords:
            if keyword in filename_lower:
                metadata['event_keyword'] = keyword
                break
        
        return metadata
    
    def get_external_platform(self, url: str) -> Optional[str]:
        """Get the external platform name from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if 'youtube.com' in domain or 'youtu.be' in domain:
                return 'youtube'
            elif 'vimeo.com' in domain:
                return 'vimeo'
            elif 'dailymotion.com' in domain:
                return 'dailymotion'
            elif 'twitch.tv' in domain:
                return 'twitch'
            else:
                return 'external'
        except:
            return 'external'
    
    def categorize_media(self, metadata: Dict) -> List[str]:
        """Categorize media based on filename and path."""
        categories = []
        filename = metadata['filename'].lower()
        path = metadata['path'].lower()
        
        # Media type categories
        if metadata['media_type'] == 'video':
            categories.append('Videos')
        elif metadata['media_type'] == 'external_video':
            categories.append('External Videos')
        elif metadata['media_type'] == 'photo':
            categories.append('Photos')
        
        # Event-based categories
        if any(word in filename or word in path for word in ['international', 'champ']):
            categories.append('Championships')
        elif any(word in filename or word in path for word in ['annual', 'regatta']):
            categories.append('Regattas')
        elif any(word in filename or word in path for word in ['frostbite']):
            categories.append('Frostbite')
        elif any(word in filename or word in path for word in ['heritage']):
            categories.append('Heritage')
        
        # Location-based categories (normalized)
        if any(word in filename or word in path for word in ['tayc', 'tred avon']):
            categories.append(self.utils.normalize_category_name('TAYC'))
        elif any(word in filename or word in path for word in ['cryc', 'corsica']):
            categories.append(self.utils.normalize_category_name('CRYC'))
        elif any(word in filename or word in path for word in ['giys', 'greenwich']):
            categories.append(self.utils.normalize_category_name('GIYS'))
        elif any(word in filename or word in path for word in ['beachwood', 'byc', 'baltimore']):
            categories.append(self.utils.normalize_category_name('BYC'))
        
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
    
    def load_analysis_data(self) -> Dict:
        """Load the photo analysis data."""
        analysis_file = Path("tmp/gallery_analysis.json")
        if not analysis_file.exists():
            print("Error: tmp/gallery_analysis.json not found. Run analyze_photos.py first.")
            return {}
        
        with open(analysis_file, 'r') as f:
            return json.load(f)
    
    def filter_excluded_media(self, media_list: List[Dict]) -> List[Dict]:
        """Filter out media based on exclusion rules."""
        filtered = []
        excluded_count = 0
        excluded_by_path = 0
        excluded_by_size = 0
        
        for media in media_list:
            excluded = False
            reason = ""
            
            # Check path exclusions
            if self.is_excluded_path(Path(media['path'])):
                excluded = True
                excluded_by_path += 1
                reason = "path exclusion"
            
            # Check size exclusions
            elif self.is_excluded_by_size(media.get('size', 0)):
                excluded = True
                excluded_by_size += 1
                reason = "size exclusion"
            
            if excluded:
                excluded_count += 1
                print(f"Excluding ({reason}): {media['path']}")
            else:
                filtered.append(media)
        
        if excluded_count > 0:
            print(f"Excluded {excluded_count} media items:")
            if excluded_by_path > 0:
                print(f"  - {excluded_by_path} by path exclusion")
            if excluded_by_size > 0:
                print(f"  - {excluded_by_size} by size exclusion")
        
        return filtered
    
    def generate_credit_stats(self, media_items: List[Dict]) -> Dict:
        """Generate statistics about photo/video credits."""
        credit_counts = defaultdict(int)
        total_credited = 0
        total_unknown = 0
        
        for media in media_items:
            credit = media.get('credit', 'Unknown photographer')
            credit_counts[credit] += 1
            
            if credit == 'Unknown photographer':
                total_unknown += 1
            else:
                total_credited += 1
        
        # Get top 10 most common credits
        top_credits = sorted(credit_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_credited': total_credited,
            'total_unknown': total_unknown,
            'unique_credits': len(credit_counts),
            'top_credits': top_credits,
            'credit_breakdown': dict(credit_counts)
        }
    
    def organize_media(self, media_list: List[Dict]):
        """Organize media by categories, events, and years."""
        for media in media_list:
            # Add to year-based organization
            if 'year' in media:
                self.years[media['year']].append(media)
            
            # Add to event-based organization
            if 'event_keyword' in media:
                self.events[media['event_keyword']].append(media)
            
            # Add to category-based organization
            categories = self.categorize_media(media)
            for category in categories:
                self.categories[category].append(media)
    
    def generate_gallery_data(self, analysis_data: Dict) -> Dict:
        """Generate structured data for the gallery."""
        photos = analysis_data.get('photos', [])
        
        # Filter out excluded media
        filtered_photos = self.filter_excluded_media(photos)
        
        # Convert to media items with enhanced metadata
        media_items = []
        for photo in filtered_photos:
            media_metadata = self.extract_metadata(
                photo['path'], 
                photo.get('size', 0), 
                photo.get('modified', '')
            )
            media_items.append(media_metadata)
        
        # Organize media
        self.organize_media(media_items)
        
        # Create summary statistics
        stats = {
            'total_media': len(media_items),
            'total_duplicates_removed': analysis_data.get('total_duplicates', 0),
            'photos': len([m for m in media_items if m['media_type'] == 'photo']),
            'videos': len([m for m in media_items if m['media_type'] == 'video']),
            'external_videos': len([m for m in media_items if m['media_type'] == 'external_video']),
            'categories_count': len(self.categories),
            'years_count': len(self.years),
            'events_count': len(self.events),
            'date_range': {
                'earliest': min(self.years.keys()) if self.years else 'unknown',
                'latest': max(self.years.keys()) if self.years else 'unknown'
            },
            'credits': self.generate_credit_stats(media_items)
        }
        
        # Create gallery collections
        collections = {
            'featured': {
                'title': 'Featured Media',
                'description': 'Highlights from recent events',
                'media': [m for m in media_items if m.get('year') and int(m['year']) >= 2020][:20]
            },
            'championships': {
                'title': 'Championships',
                'description': 'International and North American Championships',
                'media': [m for m in media_items if 'Championships' in self.categorize_media(m)]
            },
            'videos': {
                'title': 'Videos',
                'description': 'All video content',
                'media': [m for m in media_items if m['media_type'] in ['video', 'external_video']]
            },
            'historical': {
                'title': 'Historical Media',
                'description': 'Media from the early years of the Penguin Class',
                'media': [m for m in media_items if m.get('year') and int(m['year']) < 2010]
            }
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
            'platforms': set(),
            'keywords': set()
        }
        
        for media in media_items:
            if media.get('location') and media['location'] != 'unknown':
                terms['locations'].add(media['location'])
            if media.get('event_type') and media['event_type'] != 'general':
                terms['event_types'].add(media['event_type'])
            if media.get('year'):
                terms['years'].add(str(media['year']))
            if media.get('media_type'):
                terms['media_types'].add(media['media_type'])
            if media.get('external_platform'):
                terms['platforms'].add(media['external_platform'])
            
            # Extract keywords from filename
            filename_words = re.findall(r'\b[a-zA-Z]+\b', media['filename'].lower())
            terms['keywords'].update(filename_words)
        
        # Convert sets to sorted lists
        return {k: sorted(list(v)) for k, v in terms.items()}
    
    def analyze(self):
        """Run the complete analysis."""
        print("Loading media analysis data...")
        analysis_data = self.load_analysis_data()
        
        if not analysis_data:
            return {}
        
        print("Generating enhanced gallery data structure...")
        gallery_data = self.generate_gallery_data(analysis_data)
        
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
    print(f"Categories: {stats['categories_count']}")
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